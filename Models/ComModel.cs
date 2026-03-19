using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Text.Json.Serialization;
using System.Threading.Tasks;
using System.IO.Ports;

namespace Printgloo.Models
{
    public class ComModel : INotifyPropertyChanged
    {
        #region Data Members

        private string[] _Ports;
        public string[] Ports
        {
            get { return _Ports; }
            set
            {
                _Ports = value;
                OnPropertyChanged(nameof(Ports));
            }
        }

        private string _selectedPort;
        public string selectedPort
        {
            get { return _selectedPort; }
            set
            {
                _selectedPort = value;
                OnPropertyChanged(nameof(selectedPort));
            }
        }

        private bool _printerConnected = false;
        public bool printerConnected
        {
            get { return _printerConnected; }
            set
            {
                _printerConnected = value;
                OnPropertyChanged(nameof(printerConnected));
            }
        }

        private int _Ack = 0;
        public int Ack
        {
            get { return _Ack; }
            set
            {
                _Ack = value;
                OnPropertyChanged(nameof(Ack));
            }
        }

        #region OpRun

        private bool _OpRun = false;
        public bool OpRun
        {
            get { return _OpRun; }
            set
            {
                _OpRun = value;
                OnPropertyChanged(nameof(OpRun));
            }
        }

        private bool _isLog = false;
        public bool isLog
        {
            get { return _isLog; }
            set
            {
                _isLog = value;
                OnPropertyChanged(nameof(isLog));
            }
        }

        #endregion

        #region Temerature

        private double _SetTemp1 = 200;
        public double SetTemp1
        {
            get { return _SetTemp1; }
            set
            {
                _SetTemp1 = value;
                OnPropertyChanged(nameof(SetTemp1));
            }
        }

        private double _SetTemp2 = 200;
        public double SetTemp2
        {
            get { return _SetTemp2; }
            set
            {
                _SetTemp2 = value;
                OnPropertyChanged(nameof(SetTemp2));
            }
        }

        private double _SetTemp3 = 200;
        public double SetTemp3
        {
            get { return _SetTemp3; }
            set
            {
                _SetTemp3 = value;
                OnPropertyChanged(nameof(SetTemp3));
            }
        }

        private double _SetTemp4 = 200;
        public double SetTemp4
        {
            get { return _SetTemp4; }
            set
            {
                _SetTemp4 = value;
                OnPropertyChanged(nameof(SetTemp4));
            }
        }

        private double _Temp1 = -15;
        public double Temp1
        {
            get { return _Temp1; }
            set
            {
                _Temp1 = Math.Round(value, 2);
                OnPropertyChanged(nameof(Temp1));
            }
        }

        private double _Temp2 = -15;
        public double Temp2
        {
            get { return _Temp2; }
            set
            {
                _Temp2 = Math.Round(value, 2);
                OnPropertyChanged(nameof(Temp2));
            }
        }

        private double _Temp3 = -15;
        public double Temp3
        {
            get { return _Temp3; }
            set
            {
                _Temp3 = Math.Round(value, 2);
                OnPropertyChanged(nameof(Temp3));
            }
        }

        private double _Temp4 = -15;
        public double Temp4
        {
            get { return _Temp4; }
            set
            {
                _Temp4 = Math.Round(value, 2);
                OnPropertyChanged(nameof(Temp4));
            }
        }

        private bool _Temp1On = false;
        public bool Temp1On
        {
            get { return _Temp1On; }
            set
            {
                if (_Temp1On != value)
                {
                    _Temp1On = value;
                    OnPropertyChanged(nameof(Temp1On));
                }
            }
        }

        private bool _Temp2On = false;
        public bool Temp2On
        {
            get { return _Temp2On; }
            set
            {
                if (_Temp2On != value)
                {
                    _Temp2On = value;
                    OnPropertyChanged(nameof(Temp2On));
                }
            }
        }

        private bool _Temp3On = false;
        public bool Temp3On
        {
            get { return _Temp3On; }
            set
            {
                if (_Temp3On != value)
                {
                    _Temp3On = value;
                    OnPropertyChanged(nameof(Temp3On));
                }
            }
        }

        private bool _Temp4On = false;
        public bool Temp4On
        {
            get { return _Temp4On; }
            set
            {
                if (_Temp4On != value)
                {
                    _Temp4On = value;
                    OnPropertyChanged(nameof(Temp4On));
                }
            }
        }

        private string _CurrT = "1";
        public string CurrT
        {
            get { return _CurrT; }
            set
            {
                _CurrT = value;
                OnPropertyChanged(nameof(CurrT));
            }
        }

        private bool _isTuning;
        public bool isTuning
        {
            get { return _isTuning; }
            set
            {
                if (_isTuning != value)
                {
                    _isTuning = value;
                    OnPropertyChanged(nameof(isTuning));
                }
            }
        }

        #endregion

        #endregion

        #region Initialization

        public ComModel()
        {
            isTuning = false;
            Ports = SerialPort.GetPortNames();
            if (Ports.Count() > 0) selectedPort = Ports[0];
        }

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
