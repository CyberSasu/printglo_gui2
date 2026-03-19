using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Text.Json.Serialization;
using System.Threading.Tasks;
using static System.Runtime.InteropServices.JavaScript.JSType;

namespace Printgloo.Models
{
    public class ValueModel : INotifyPropertyChanged
    {
        #region Data Members

        //Temp
        public double MinTemp { get; set; }

        public double MaxTemp { get; set; }

        private int _TuningTemp;
        public int TuningTemp
        {
            get { return _TuningTemp; }
            set
            {
                if (_TuningTemp != value)
                {
                    _TuningTemp = Math.Clamp(value, 50, 450);
                    OnPropertyChanged(nameof(TuningTemp));
                }
            }
        }

        private int _TuningCycles;
        public int TuningCycles
        {
            get { return _TuningCycles; }
            set
            {
                if (_TuningCycles != value)
                {
                    _TuningCycles = Math.Clamp(value, 1, 30);
                    OnPropertyChanged(nameof(TuningCycles));
                }
            }
        }

        private double _TuningP;
        public double TuningP
        {
            get { return _TuningP; }
            set
            {
                if (_TuningP != value)
                {
                    _TuningP = value;
                    OnPropertyChanged(nameof(TuningP));
                }
            }
        }

        private double _TuningI;
        public double TuningI
        {
            get { return _TuningI; }
            set
            {
                if (_TuningI != value)
                {
                    _TuningI = value;
                    OnPropertyChanged(nameof(TuningI));
                }
            }
        }

        private double _TuningD;
        public double TuningD
        {
            get { return _TuningD; }
            set
            {
                if (_TuningD != value)
                {
                    _TuningD = value;
                    OnPropertyChanged(nameof(TuningD));
                }
            }
        }

        //Manual

        private int _Fan1;
        public int Fan1
        {
            get { return _Fan1; }
            set
            {
                _Fan1 = Math.Clamp(value, 0, 100);
                OnPropertyChanged(nameof(Fan1));
            }
        }

        private int _Fan2;
        public int Fan2
        {
            get { return _Fan2; }
            set
            {
                _Fan2 = Math.Clamp(value, 0, 100);
                OnPropertyChanged(nameof(Fan2));
            }
        }

        private int _Fan3;
        public int Fan3
        {
            get { return _Fan3; }
            set
            {
                _Fan3 = Math.Clamp(value, 0, 100);
                OnPropertyChanged(nameof(Fan3));
            }
        }

        private double _Auger;
        public double Auger
        {
            get { return _Auger; }
            set
            {
                if (_Auger != value)
                {
                    _Auger = Math.Clamp(value, 0, 150);
                    OnPropertyChanged(nameof(Auger));
                }
            }
        }
        
        private double _Winder;
        public double Winder
        {
            get { return _Winder; }
            set
            {
                if (_Winder != value)
                {
                    _Winder = Math.Clamp(value, 0, 300);
                    OnPropertyChanged(nameof(Winder));
                }
            }
        }
        
        private double _Spooler;
        public double Spooler
        {
            get { return _Spooler; }
            set
            {
                if (_Spooler != value)
                {
                    _Spooler = Math.Clamp(value, 0, 20);
                    OnPropertyChanged(nameof(Spooler));
                }
            }
        }

        [JsonIgnore]
        public double CalcWinder;
        
        private double _WinderMax;
        public double WinderMax
        {
            get { return _WinderMax; }
            set
            {
                if (_WinderMax != value)
                {
                    _WinderMax = Math.Clamp(value, 0, 120);
                    OnPropertyChanged(nameof(WinderMax));
                }
            }
        }
        
        private double _SpoolerID;
        public double SpoolerID
        {
            get { return _SpoolerID; }
            set
            {
                if (_SpoolerID != value)
                {
                    _SpoolerID = Math.Clamp(value, 0, double.MaxValue);
                    OnPropertyChanged(nameof(SpoolerID));
                }
            }
        }
        
        private double _SpoolerOD;
        public double SpoolerOD
        {
            get { return _SpoolerOD; }
            set
            {
                if (_SpoolerOD != value)
                {
                    _SpoolerOD = Math.Clamp(value, 0, double.MaxValue);
                    OnPropertyChanged(nameof(SpoolerOD));
                }
            }
        }

        private double _Puller;
        public double Puller
        {
            get { return _Puller; }
            set
            {
                if (_Puller != value)
                {
                    _Puller = Math.Clamp(value, 0, 300);
                    OnPropertyChanged(nameof(Puller));
                }
            }
        }

        private double _WinderStart;
        public double WinderStart
        {
            get { return _WinderStart; }
            set
            {
                if (_WinderStart != value)
                {
                    _WinderStart = Math.Clamp(value, double.MinValue, double.MaxValue);
                    OnPropertyChanged(nameof(WinderStart));
                }
            }
        }

        public double PullerDia { get; set; }
       
        public double Spmm { get; set; }
       
        public double SpoolerSpmm { get; set; }
       
        public double WinderSpmm { get; set; }
       
        public double WinderPitch { get; set; }

        //Automatic
        public double PullerP { get; set; }
        
        public double PullerI { get; set; }
        
        public double PullerD { get; set; }

        public int PIDInterval { get; set; }

        [JsonIgnore]
        public double LastPullerD { get; set; }

        public double MinPID { get; set; }
        
        public double MaxPID { get; set; }
        
        public double IntegratorWindPID { get; set; }

        public double K1 { get; set; }

        public double K2 {  get; set; }

        public double dia_iState_fwidth { get; set; }

        public double puller_increment { get; set; }

        //Op
        private double _FDia;
        public double FDia
        {
            get { return _FDia; }
            set
            {
                if (_FDia != value)
                {
                    _FDia = value;
                    OnPropertyChanged(nameof(FDia));
                }
            }
        }

        [JsonIgnore]
        public List<double> CurrFDia = new List<double> ();

        [JsonIgnore]
        public double LastFDia { get; set; }

        private double _ReadFDia;
        [JsonIgnore]
        public double ReadFDia
        {
            get { return _ReadFDia; }
            set
            {
                _ReadFDia = value;
                OnPropertyChanged(nameof(ReadFDia));
            }
        }
        
        public int OpDelay { get; set; }
        
        #endregion

        #region Functions

        public ValueModel()
        {

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
