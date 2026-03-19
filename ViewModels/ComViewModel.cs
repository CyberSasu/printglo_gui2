using Printgloo.Models;
using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.ComponentModel;
using System.Diagnostics;
using System.IO;
using System.IO.Ports;
using System.Linq;
using System.Printing;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Media.Media3D;
using System.Windows.Threading;
using static System.Runtime.InteropServices.JavaScript.JSType;

namespace Printgloo.ViewModels
{
    public class ComViewModel : INotifyPropertyChanged
    {
        #region Data Members

        //Serial Data
        private SerialPort serialPort;
        private CancellationTokenSource cancellationTokenSource;

        //Communication Data
        private ConcurrentQueue<string> linesToSend = new ConcurrentQueue<string>();
        private ConcurrentQueue<string> uiReceivedQueue = new ConcurrentQueue<string>();
        private ConcurrentQueue<string> uiSentQueue = new ConcurrentQueue<string>();

        //Action Event
        public event Action<string> OnCommandSent;
        public event Action<string> OnResponseReceived;

        private SettingModel _Setting;
        public SettingModel Setting
        {
            get { return _Setting; }
            set
            {
                _Setting = value;
                OnPropertyChanged(nameof(Setting)); 
            }
        }

        private ComModel _comModel;
        public ComModel comModel
        {
            get { return _comModel; }
            set
            {
                _comModel = value;
                OnPropertyChanged(nameof(comModel));
            }
        }

        public bool isWinderAuto = false;

        public bool isSpoolerAuto = false;

        public bool isPullerAuto = false;

        public double AugerRPM = 0, SpoolerRPM = 0, WinderRPM = 0, PullerRPM = 0;

        #endregion

        #region Initialization

        public ComViewModel(SettingModel sm)
        {
            this.Setting = sm;
            comModel = new ComModel();
        }

        #endregion

        #region Functions

        public void ComChecks()
        {
            comModel.Ports = SerialPort.GetPortNames();
        }

        #region Connection / Disconnection

        public void SetInitialConnectState()
        {
            comModel.OpRun = false;
            comModel.Ack = 0;
            linesToSend = new ConcurrentQueue<string>();
            comModel.printerConnected = true;
            comModel.Temp1On = false;
            comModel.Temp2On = false;
            comModel.Temp3On = false;
            comModel.Temp4On = false;

            SendCommand(Setting.commands.TempRead, "5");
        }

        public async Task<bool> ConnectCom()
        {
            //return true;
            if (comModel.selectedPort == null)
            {
                comModel.printerConnected = false;
                MessageBox.Show("Select a com port");
                return false;
            }

            if (!await ConnectBoard())
            {
                comModel.printerConnected = false;
                serialPort = null;
                MessageBox.Show("Printer failed to connect");
                return false;
            }
            StartCommunication();

            return true;
        }

        private async Task<bool> ConnectBoard()
        {
            try
            {
                serialPort = new SerialPort();
                serialPort.PortName = comModel.selectedPort;
                serialPort.BaudRate = 250000;
                serialPort.Parity = Parity.None;
                serialPort.StopBits = StopBits.One;
                serialPort.DataBits = 8;
                serialPort.Handshake = Handshake.None;
                serialPort.WriteTimeout = 500;
                serialPort.DtrEnable = true;
                serialPort.RtsEnable = true;

                serialPort.Open();
                serialPort.DiscardInBuffer();
                serialPort.DiscardOutBuffer();

                await Task.Delay(1000);
                return true;
            }
            catch (IOException ex)
            {
                return false;
            }
            catch (System.UnauthorizedAccessException ex)
            {
                return false;
            }
            catch (Exception ex)
            {
                return false;
            }
        }

        public async Task<bool> ComClose()
        {
            OpDisrupt();
            comModel.printerConnected = false;
            if (cancellationTokenSource != null && !cancellationTokenSource.IsCancellationRequested) cancellationTokenSource.Cancel();

            if (serialPort != null && serialPort.IsOpen)
            {
                serialPort.Close();
                serialPort.Dispose();
                serialPort = null;
                return false;
            }
            if (cancellationTokenSource != null && !cancellationTokenSource.IsCancellationRequested) cancellationTokenSource.Dispose();
            return true;
        }

        public void EmergencyStop()
        {
            OpDisrupt();
            Thread.Sleep(1000);
        }

        private void StartCommunication()
        {
            comModel.OpRun = false;
            comModel.isTuning = false;

            cancellationTokenSource = new CancellationTokenSource();

            //Communication received
            Thread serialReceiverThread = new Thread(SerialReceiver);
            serialReceiverThread.Start();
            Task.Run(() => UICommandReceivedUpdateTask(), cancellationTokenSource.Token);

            //Communication Sent
            Task.Run(() => SerialSender(), cancellationTokenSource.Token);
            Task.Run(() => UICommandSentUpdateTask(), cancellationTokenSource.Token);
        }

        #endregion

        #region MKS Receiving functionality

        private void SerialReceiver()
        {
            StringBuilder buffer = new StringBuilder();
            char[] readBuffer = new char[1024];

            while (!cancellationTokenSource.Token.IsCancellationRequested)
            {
                try
                {
                    if (serialPort.BytesToRead > 0)
                    {
                        string data = serialPort.ReadExisting();
                        foreach (char ch in data)
                        {
                            if (ch == '\n')
                            {
                                string line = buffer.ToString().Trim();
                                buffer.Clear();

                                if (line.Contains("ok")) comModel.Ack--;
                                if (line.Count() > 1) uiReceivedQueue.Enqueue(line);
                            }
                            else
                            {
                                buffer.Append(ch);
                            }
                        }
                    }
                }
                catch
                {
                    ComClose();
                    break;
                }
            }
        }

        private async Task UICommandReceivedUpdateTask()
        {
            while (!cancellationTokenSource.Token.IsCancellationRequested)
            {
                if (uiReceivedQueue.TryDequeue(out string response))
                {
                    switch (response)
                    {
                        case var _ when response.Contains("AUGER ERROR"):
                            comModel.printerConnected = false;
                            break;

                        case var _ when response.Contains("PID Autotune finished!"):
                            _ = Task.Run(() => SetPID());
                            break;

                        case var _ when response.Contains("Printer halted"):
                            comModel.printerConnected = false;
                            MessageBox.Show("Connect to machine again.\nPlug out and Plug in the power of the machine and restart the software again if it happens again.\nIf issue persists contact the team");
                            break;

                        case var _ when response.Contains("Filament dia"):
                            Setting.values.ReadFDia = Convert.ToDouble(response.Split(":").Last());
                            Setting.values.CurrFDia.Add(Setting.values.ReadFDia);
                            if (isPullerAuto && comModel.OpRun) if(Setting.values.CurrFDia.Count > Setting.values.PIDInterval) SetNewPuller();
                            break;

                        case var _ when response.Contains("Kp:"):
                            _ = Task.Run(() => GetPID(response));
                            break;

                        case var _ when response.Contains("T:"):
                        case var _ when response.Contains("T1:"):
                            _ = Task.Run(() => GetTemp(response));
                            break;

                        default:
                            break;
                    }

                    OnResponseReceived?.Invoke(response);
                }

                // Add a small delay to prevent tight looping
                await Task.Delay(5);
            }
        }

        #endregion

        #region MKS Sending functionality

        private async Task SerialSender()
        {
            var stringBuilder = new StringBuilder();

            while (!cancellationTokenSource.Token.IsCancellationRequested)
            {
                try
                {
                    if (linesToSend.TryDequeue(out string command))
                    {
                        Send(command);
                        await Task.Delay(10);
                    }
                }
                catch
                {
                    ComClose();
                    break;
                }
            }
        }

        private async Task UICommandSentUpdateTask()
        {
            while (!cancellationTokenSource.Token.IsCancellationRequested)
            {
                if (uiSentQueue.TryDequeue(out string command))
                {
                    OnCommandSent?.Invoke(command);
                }

                // Add a small delay to prevent tight looping
                await Task.Delay(20);
            }
        }

        #endregion

        #region Op Running

        public void StartOp()
        {
            if (serialPort?.IsOpen != true) return;

            comModel.OpRun = true;
            Task.Run(() => SerialOpThread(), cancellationTokenSource.Token);
        }

        private async Task SerialOpThread()
        {
            int j = 0;
            int i = 0;
            int wc = 1;
            SendCommand(Setting.commands.Winder, "600");
            await Task.Delay(1000);
            Send(Setting.commands.OpPreset);
            await Task.Delay(1000);
            while (comModel.Ack > 0)
            {
            await Task.Delay(1000);
            }
            SendCommand(Setting.commands.WinderMove, (Setting.values.WinderStart).ToString());
            SendCommand(Setting.commands.WinderSetPos, "0");
            SendCommand(Setting.commands.Winder, (WinderRPM).ToString());

            while (comModel.OpRun && !cancellationTokenSource.Token.IsCancellationRequested)
            {
                try
                {
                    if (i >= Setting.values.CalcWinder)
                    {
                        wc = -wc;
                        i = 0;
                        j++;
                        if (j >= 2)
                        {
                            Setting.values.SpoolerID = Setting.values.SpoolerID + (2 * Setting.values.FDia);
                            j = 0;
                            if (isSpoolerAuto) MotorControl("Spooler");
                        }
                    }
                    i++;

                    ParseSend(Setting.commands.OpMotion, $"{wc}");
                    Send(Setting.commands.FRead);
                    if (comModel.isLog) Logger.Log($"FilamentDia : {Setting.values.ReadFDia}, AugerRPM : {AugerRPM}, PullerRPM : {PullerRPM}, SpoolerRPM : {SpoolerRPM}, WinderRPM : {WinderRPM}, T1 : {comModel.Temp1}, T2 : {comModel.Temp2}, T3 : {comModel.Temp3}, T4 : {comModel.Temp4}");
                    await Task.Delay(Setting.values.OpDelay);
                }
                catch
                {
                    OpDisrupt();
                    break;
                }
            }
        }

        public void StopOp()
        {
            OpDisrupt(); 
        }

        public void OpDisrupt()
        {
            comModel.OpRun = false;
            comModel.Ack = 0;
            linesToSend = new ConcurrentQueue<string>();

            SendCommand(Setting.commands.StopMotion);
        }

        #endregion

        #region Data Process

        public string Printgaps(string input)
        {
            if (input.Contains(";")) input = input.Replace(";", "");
            string pattern = @"\s+";
            string replacement = " ";
            string result = Regex.Replace(input, pattern, replacement);
            result = result.Trim();
            return result;
        }

        public string RemoveExcessiveGaps(string input)
        {
            if (input.Contains(";")) input = input.Replace(";", "");
            string pattern = @"\s+";
            string replacement = " ";
            string result = Regex.Replace(input, pattern, replacement);
            result = result.ToUpper();
            result = result.Trim();
            result += ";";
            return result;
        }

        public static double ExtractValue(string input, string variable)
        {
            string pattern = variable + @"(-?\d+(?:\.\d+)?|-?\.\d+)";
            if (input.Contains(':')) pattern = variable + @":(-?\d+(?:\.\d+)?|-?\.\d+)";
            if (input.Contains('=')) pattern = variable + @"=(-?\d+(?:\.\d+)?|-?\.\d+)";
            Match match = Regex.Match(input, pattern);

            if (match.Success)
            {
                return Math.Round(double.Parse(match.Groups[1].Value), 2);
            }

            // Return a default value (0.0 in this case) if the variable is not found
            return 0.0;
        }

        public static double ExtractPID(string input, string variable)
        {
            string pattern = variable + @"\s*[:=]?\s*(-?\d+(?:\.\d+)?|-?\.\d+)";
            Match match = Regex.Match(input, pattern, RegexOptions.IgnoreCase);

            if (match.Success)
            {
                return Math.Round(double.Parse(match.Groups[1].Value), 2);
            }

            return 0.0;
        }

        public void GetPID(string st)
        {
            Setting.values.TuningP = ExtractPID(st, "Kp");
            Setting.values.TuningI = ExtractPID(st, "Ki");
            Setting.values.TuningD = ExtractPID(st, "Kd");
        }

        private void GetTemp(string st)
        {
            comModel.Temp1 = st.Contains($"{Setting.commands.Temp1Text}:") ? ExtractValue(st, Setting.commands.Temp1Text) : -15;
            comModel.Temp2 = st.Contains($"{Setting.commands.Temp2Text}:") ? ExtractValue(st, Setting.commands.Temp2Text) : -15;
            comModel.Temp3 = st.Contains($"{Setting.commands.Temp3Text}:") ? ExtractValue(st, Setting.commands.Temp3Text) : -15;
            comModel.Temp4 = st.Contains($"{Setting.commands.Temp4Text}:") ? ExtractValue(st, Setting.commands.Temp4Text) : -15;
            
            if (comModel.Temp1 == -15 && comModel.Temp1On) 
                TempOff("1");
            if (comModel.Temp2 == -15 && comModel.Temp2On) 
                TempOff("2");
            if (comModel.Temp3 == -15 && comModel.Temp3On) 
                TempOff("3");
            if (comModel.Temp4 == -15 && comModel.Temp4On) 
                TempOff("4");
        }

        #endregion

        #region Temperature

        public void StartTuning()
        {
            AllTempOff();
            int e = comModel.CurrT switch
            {
                "1" => -1,
                "2" => 0,
                "3" => -2,
                "4" => 1
            };
            SendCommand($"M303 E{e} C{Setting.values.TuningCycles} S{Setting.values.TuningTemp}");
            comModel.isTuning = true;
        }

        public void SetPID()
        {
            string c = comModel.CurrT switch
            {
                "1" => "M304 ",
                "2" => "M301 ",
                "3" => "M309 ",
                "4" => "M301 "
            };
            SendCommand(c + $"P{Setting.values.TuningP} I{Setting.values.TuningI} D{Setting.values.TuningD}");
            SendCommand("M500");
            comModel.isTuning = false;
            MessageBox.Show($"Pid Tuning is saved for T{comModel.CurrT}");
        }

        public void TempOn(string tag)
        {
            switch (tag)
            {
                case "1":
                    SendCommand(Setting.commands.Temp1On, $"{comModel.SetTemp1}");
                    comModel.Temp1On = true;
                    break;
                case "2":
                    SendCommand(Setting.commands.Temp2On, $"{comModel.SetTemp2}");
                    comModel.Temp2On = true;
                    break;
                case "3":
                    SendCommand(Setting.commands.Temp3On, $"{comModel.SetTemp3}");
                    comModel.Temp3On = true;
                    break;
                case "4":
                    SendCommand(Setting.commands.Temp4On, $"{comModel.SetTemp4}");
                    comModel.Temp4On = true;
                    break;
            }
        }

        public void TempOff(string tag)
        {
            switch (tag)
            {
                case "1":
                    comModel.Temp1On = false;
                    SendCommand(Setting.commands.Temp1Off);
                    break;
                case "2":
                    comModel.Temp2On = false;
                    SendCommand(Setting.commands.Temp2Off);
                    break;
                case "3":
                    comModel.Temp3On = false;
                    SendCommand(Setting.commands.Temp3Off);
                    break;
                case "4":
                    comModel.Temp4On = false;
                    SendCommand(Setting.commands.Temp4Off);
                    break;
            }
        }

        public void AllTempOff()
        {
            if (comModel.Temp1On) TempOff("1");
            if (comModel.Temp2On) TempOff("2");
            if (comModel.Temp3On) TempOff("3");
            if (comModel.Temp4On) TempOff("4");
        }

        #endregion

        #region Control functionality

        public void MotorControl(string motor = "")
        {
            switch (motor)
            {
                case "Auger":
                    AugerRPM = Math.Round(Setting.values.Auger * Setting.values.Spmm / 60, 2);
                    SendCommand(Setting.commands.Auger, (AugerRPM).ToString());
                    break;
                case "Winder":
                    WinderRPM = Math.Round(Setting.values.Winder, 2);
                    Setting.values.CalcWinder = Math.Round(Math.Floor((Setting.values.WinderSpmm * Setting.values.WinderMax) / WinderRPM), 0);
                    SendCommand(Setting.commands.Winder, (WinderRPM).ToString());
                    break;
                case "Spooler":
                    var s = Setting.values.Puller * Setting.values.PullerDia / Setting.values.SpoolerID;
                    SpoolerRPM = Math.Round(s * Setting.values.SpoolerSpmm / 60, 2);
                    SendCommand(Setting.commands.Spooler, (SpoolerRPM).ToString());
                    if (isWinderAuto)
                    {
                        WinderRPM = Math.Round(SpoolerRPM * Setting.values.WinderPitch, 2);
                        Setting.values.CalcWinder = Math.Round(Math.Floor((Setting.values.WinderSpmm * Setting.values.WinderMax) / WinderRPM), 0);
                        SendCommand(Setting.commands.Winder, (WinderRPM).ToString());
                    }
                    break;
                case "Spool":
                    SpoolerRPM = Math.Round(Setting.values.Spooler * Setting.values.SpoolerSpmm / 60, 2);
                    SendCommand(Setting.commands.Spooler, (SpoolerRPM).ToString());
                    if (isWinderAuto)
                    {
                        WinderRPM = Math.Round(SpoolerRPM * Setting.values.WinderPitch, 2);
                        Setting.values.CalcWinder = Math.Round(Math.Floor((Setting.values.WinderSpmm * Setting.values.WinderMax) / WinderRPM), 0);
                        SendCommand(Setting.commands.Winder, (WinderRPM).ToString());
                    }
                    break;
                default:
                    PullerRPM = Math.Round(Setting.values.Puller * Setting.values.Spmm / 60, 2);
                    SendCommand(Setting.commands.Puller, (PullerRPM).ToString());
                    if (isSpoolerAuto) MotorControl("Spooler");
                    break;
            }
        }

        public void FanControl(bool isOn, int fan = 0)
        {
            double intensity = 0;
            switch (fan)
            {
                case 1:
                    if (isOn)
                    {
                        SendCommand(Setting.commands.Fan1);
                        return;
                    }
                    intensity = Setting.values.Fan1 * 2.55;
                    SendCommand(Setting.commands.Fan1, (Math.Round(intensity, 1)).ToString());
                    break;
                case 2:
                    if (isOn)
                    {
                        SendCommand(Setting.commands.Fan2);
                        return;
                    }
                    intensity = Setting.values.Fan2 * 2.55;
                    SendCommand(Setting.commands.Fan2, (Math.Round(intensity, 1)).ToString());
                    break;
                case 3:
                    if (isOn)
                    {
                        SendCommand(Setting.commands.Fan3);
                        return;
                    }
                    intensity = Setting.values.Fan3 * 2.55;
                    SendCommand(Setting.commands.Fan3, (Math.Round(intensity, 1)).ToString());
                    break;
            }
        }

        public void CustomSends(string command)
        {
            if (serialPort?.IsOpen == true) SendCommand(command);
        }

        public void ParseCommand(string command, string value = "0")
        {
            if (command.Length < 2) return;
            command = RemoveExcessiveGaps(command);
            if (command.Contains("{}")) command = command.Replace("{}", value);
            linesToSend.Enqueue(command);
        }

        public void SendCommand(string command, string value = "0")
        {
            if (command == null) return;
            string[] parts = command.Split(',');
            if (parts.Length == 1)
            {
                ParseCommand(command, value);
            }
            else
            {
                for (int i = 0; i < parts.Length; i++)
                {
                    ParseCommand(parts[i], value);
                }
            }
        }

        public void ParseSend(string command, string value = "0")
        {
            if (command.Contains("{}")) command = command.Replace("{}", value);
            Send(command);
        }

        public void Send(string command)
        {
            if (serialPort == null) return;
            serialPort.WriteLine(command);
            comModel.Ack++;
            uiSentQueue.Enqueue(command);
        }

        #endregion

        #region PID

        public void SetNewPuller()
        {
            double filament_control = Setting.values.Puller;
            double pid_input = Setting.values.CurrFDia.Count() > 0 ? Setting.values.CurrFDia.Average() : 0;
            double pid_error_fwidth = Setting.values.FDia - pid_input;
            Setting.values.CurrFDia.Clear();

            // Proportianal
            double p = filament_control - Setting.values.PullerP * pid_error_fwidth;

            // Integral
            if ((filament_control < Setting.values.MaxPID && pid_error_fwidth < 0) || (filament_control > Setting.values.MinPID && pid_error_fwidth > 0))
            {
                Setting.values.dia_iState_fwidth += pid_error_fwidth * Setting.values.puller_increment;
                Setting.values.dia_iState_fwidth = Math.Max(Math.Min(Setting.values.dia_iState_fwidth, Setting.values.IntegratorWindPID), -Setting.values.IntegratorWindPID);
            }

            double i = Setting.values.PullerI * Setting.values.dia_iState_fwidth;

            // Derivative
            double d = (Setting.values.PullerD / Setting.values.puller_increment * (pid_input - Setting.values.LastFDia)) * Setting.values.K2 + (Setting.values.K1 * Setting.values.LastPullerD);
            Setting.values.LastPullerD = d;
            Setting.values.LastFDia = pid_input;

            // PID Output
            filament_control = p - i + d;
            filament_control = Math.Max(Math.Min(filament_control, Setting.values.MaxPID), Setting.values.MinPID);

            Setting.values.Puller = filament_control;
            MotorControl();
        }

        #endregion

        #endregion

        #region Property Changed Notification

        public event PropertyChangedEventHandler PropertyChanged;

        private void OnPropertyChanged(string property)
        {
            if (PropertyChanged != null)
            {
                PropertyChanged(this, new PropertyChangedEventArgs(property));
            }
        }

        #endregion
    }
}
