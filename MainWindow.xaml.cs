using Printgloo.Models;
using Printgloo.Resources.UserControls;
using Printgloo.ViewModels;
using System.Diagnostics;
using System.Text;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Controls.Primitives;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;

namespace Printgloo
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        #region Declarations

        //Model Declarations
        public SettingModel sett;

        //ViewModel Declarations
        public ComViewModel comViewModel;

        #endregion

        #region Initialization

        public MainWindow()
        {
            InitializeComponent();
            InitializeModels();
            InitializeViewModels();
            SetDataContexts();
            SetActions();
        }

        public void InitializeModels()
        {
            sett = new SettingModel();
            sett = sett.ReadSettings();
        }

        public void InitializeViewModels()
        {
            //Com Setup
            comViewModel = new ComViewModel(sett);
        }

        public void SetDataContexts()
        {
            this.DataContext = comViewModel;
            Ext1TempSlider.DataContext = comViewModel;
            Ext2TempSlider.DataContext = comViewModel;
            Ext3TempSlider.DataContext = comViewModel;
            Ext4TempSlider.DataContext = comViewModel;
        }

        public void SetActions()
        {
            this.Closing += AppClose;
            comViewModel.OnCommandSent += UpdateUIOnCommandSent;
            comViewModel.OnResponseReceived += UpdateUIOnResponseReceived;
        }

        #endregion

        #region Clicks

        private void CheckCom(object sender, MouseButtonEventArgs e)
        {
            comViewModel.ComChecks();
        }

        private async void ConnectCom(object sender, RoutedEventArgs e)
        {
            if (await comViewModel.ConnectCom())
            {
                comViewModel.SetInitialConnectState();
            }
        }

        private async void DisconnectCom(object sender, RoutedEventArgs e)
        {
            await comViewModel.ComClose();
        }

        private void EmergencyClick(object sender, RoutedEventArgs e)
        {
            comViewModel.EmergencyStop();
        }

        private void ReadSettClick(object sender, RoutedEventArgs e)
        {
            sett = sett.ReadSettings();
            comViewModel.Setting = sett;
        }

        private void TempClick(object sender, MouseButtonEventArgs e)
        {
            switch ((sender as RoundSlider0)?.Tag.ToString())
            {
                case "1":
                    if (comViewModel.comModel.Temp1On) comViewModel.TempOff("1");
                    else comViewModel.TempOn("1");
                    break;
                case "2":
                    if (comViewModel.comModel.Temp2On) comViewModel.TempOff("2");
                    else comViewModel.TempOn("2");
                    break;
                case "3":
                    if (comViewModel.comModel.Temp3On) comViewModel.TempOff("3");
                    else comViewModel.TempOn("3");
                    break;
                case "4":
                    if (comViewModel.comModel.Temp4On) comViewModel.TempOff("4");
                    else comViewModel.TempOn("4");
                    break;
            }
        }

        private void MotorClick(object sender, RoutedEventArgs e)
        {
            comViewModel.MotorControl((sender as Button)?.Tag.ToString());
        }

        private void FanClick(object sender, RoutedEventArgs e)
        {
            comViewModel.FanControl((sender as ToggleButton)?.IsChecked == false, Convert.ToInt32((sender as ToggleButton)?.Tag.ToString()));
        }

        private void StartTuningClick(object sender, RoutedEventArgs e)
        {
            comViewModel.StartTuning();
        }

        private void SetPIDClick(object sender, RoutedEventArgs e)
        {
            comViewModel.SetPID();
        }

        private async void StartOpClick(object sender, RoutedEventArgs e)
        {
            if (PullerToggle.IsChecked == true)
            {
                comViewModel.SetNewPuller();
                await Task.Delay(2500);
            }
            comViewModel.isWinderAuto = WinderToggle.IsChecked == true;
            comViewModel.isSpoolerAuto = SpoolerToggle.IsChecked == true;
            comViewModel.isPullerAuto = PullerToggle.IsChecked == true;
            comViewModel.StartOp();
        }

        private void StopOpClick(object sender, RoutedEventArgs e)
        {
            comViewModel.StopOp();
        }

        private void CustomClick(object sender, RoutedEventArgs e)
        {
            if (CustomCommand.Text.Length < 2) return;
            CustomSent(CustomCommand.Text);
            CustomCommand.Text = "";
        }

        private void CustomCommandEnter(object sender, KeyEventArgs e)
        {
            switch (e.Key)
            {
                case Key.Enter:
                    if (CustomCommand.Text.Length < 2) return;
                    CustomSent(CustomCommand.Text);
                    CustomCommand.Text = "";
                    break;
                case Key.Up:
                    customCommandPos--;
                    if (customCommandPos < 0) customCommandPos = 0;
                    if (customCommandPos < customCommandsHistory.Count)
                        CustomCommand.Text = customCommandsHistory.ElementAt(customCommandPos);
                    CustomCommand.SelectionLength = 0;
                    CustomCommand.SelectionStart = CustomCommand.Text.Length;
                    break;
                case Key.Down:
                    customCommandPos++;
                    if (customCommandPos >= customCommandsHistory.Count)
                    {
                        CustomCommand.Text = "";
                        customCommandPos = customCommandsHistory.Count;
                    }
                    if (customCommandPos < customCommandsHistory.Count)
                        CustomCommand.Text = customCommandsHistory.ElementAt(customCommandPos);
                    CustomCommand.SelectionLength = 0;
                    CustomCommand.SelectionStart = CustomCommand.Text.Length;
                    break;
            }
        }

        #endregion

        #region Function

        private async void AppClose(object sender, System.ComponentModel.CancelEventArgs e)
        {
            sett.WriteSettings(comViewModel.Setting);

            await comViewModel.ComClose();
            await Task.Delay(250);
            Application.Current.Shutdown();
            Environment.Exit(0);
        }

        #region Com

        public LinkedList<string> customCommandsHistory = new LinkedList<string>();
        public int customCommandPos = 0;

        private void CustomSent(string command)
        {
            comViewModel.SendCommand(command);
            customCommandsHistory.AddLast(command);
            if (customCommandsHistory.Count > 150)
                customCommandsHistory.RemoveFirst();
            customCommandPos = customCommandsHistory.Count;
        }

        public void UpdateUIOnCommandSent(string command)
        {
            Dispatcher?.InvokeAsync(() =>
            {
                var text = "Sent : " + command;
                Debug.WriteLine(text);
                serialDataSent.AppendText(text + Environment.NewLine);
                serialDataSent.ScrollToEnd();
            });
        }

        public void UpdateUIOnResponseReceived(string response)
        {
            Dispatcher?.InvokeAsync(() =>
            {
                var text = "Received : " + response;
                Debug.WriteLine(text);
                serialDataReceived.AppendText(text + Environment.NewLine);
                serialDataReceived.ScrollToEnd();
            });
        }

        #endregion

        #endregion

    }
}