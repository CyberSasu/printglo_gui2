using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Printgloo.Models
{
    public class CommandModel : INotifyPropertyChanged
    {
        #region Data Members

        private string _StopMotion;
        public string StopMotion
        {
            get { return _StopMotion; }
            set
            {
                _StopMotion = value;
                OnPropertyChanged(nameof(StopMotion));
            }
        }

        #region TempCommands

        private string _Temp1On;
        public string Temp1On
        {
            get { return _Temp1On; }
            set
            {
                _Temp1On = value;
                OnPropertyChanged(nameof(Temp1On));
            }
        }

        private string _Temp2On;
        public string Temp2On
        {
            get { return _Temp2On; }
            set
            {
                _Temp2On = value;
                OnPropertyChanged(nameof(Temp2On));
            }
        }

        private string _Temp3On;
        public string Temp3On
        {
            get { return _Temp3On; }
            set
            {
                _Temp3On = value;
                OnPropertyChanged(nameof(Temp3On));
            }
        }

        private string _Temp4On;
        public string Temp4On
        {
            get { return _Temp4On; }
            set
            {
                _Temp4On = value;
                OnPropertyChanged(nameof(Temp4On));
            }
        }

        private string _Temp1Off;
        public string Temp1Off
        {
            get { return _Temp1Off; }
            set
            {
                _Temp1Off = value;
                OnPropertyChanged(nameof(Temp1Off));
            }
        }

        private string _Temp2Off;
        public string Temp2Off
        {
            get { return _Temp2Off; }
            set
            {
                _Temp2Off = value;
                OnPropertyChanged(nameof(Temp2Off));
            }
        }

        private string _Temp3Off;
        public string Temp3Off
        {
            get { return _Temp3Off; }
            set
            {
                _Temp3Off = value;
                OnPropertyChanged(nameof(Temp3Off));
            }
        }

        private string _Temp4Off;
        public string Temp4Off
        {
            get { return _Temp4Off; }
            set
            {
                _Temp4Off = value;
                OnPropertyChanged(nameof(Temp4Off));
            }
        }

        private string _Fan1;
        public string Fan1
        {
            get { return _Fan1; }
            set
            {
                _Fan1 = value;
                OnPropertyChanged(nameof(Fan1));
            }
        }

        private string _Fan2;
        public string Fan2
        {
            get { return _Fan2; }
            set
            {
                _Fan2 = value;
                OnPropertyChanged(nameof(Fan2));
            }
        }

        private string _Fan3;
        public string Fan3
        {
            get { return _Fan3; }
            set
            {
                _Fan3 = value;
                OnPropertyChanged(nameof(Fan3));
            }
        }

        #endregion

        #region Temp Reading

        private string _TempRead;
        public string TempRead
        {
            get { return _TempRead; }
            set
            {
                _TempRead = value;
                OnPropertyChanged(nameof(TempRead));
            }
        }

        private string _Temp1Text;
        public string Temp1Text
        {
            get { return _Temp1Text; }
            set
            {
                _Temp1Text = value;
                OnPropertyChanged(nameof(Temp1Text));
            }
        }

        private string _Temp2Text;
        public string Temp2Text
        {
            get { return _Temp2Text; }
            set
            {
                _Temp2Text = value;
                OnPropertyChanged(nameof(Temp2Text));
            }
        }

        private string _Temp3Text;
        public string Temp3Text
        {
            get { return _Temp3Text; }
            set
            {
                _Temp3Text = value;
                OnPropertyChanged(nameof(Temp3Text));
            }
        }

        private string _Temp4Text;
        public string Temp4Text
        {
            get { return _Temp4Text; }
            set
            {
                _Temp4Text = value;
                OnPropertyChanged(nameof(Temp4Text));
            }
        }

        #endregion

        #region OpMotion Commands

        private string _Auger;
        public string Auger
        {
            get { return _Auger; }
            set
            {
                _Auger = value;
                OnPropertyChanged(nameof(Auger));
            }
        }

        private string _Puller;
        public string Puller
        {
            get { return _Puller; }
            set
            {
                _Puller = value;
                OnPropertyChanged(nameof(Puller));
            }
        }

        private string _Spooler;
        public string Spooler
        {
            get { return _Spooler; }
            set
            {
                _Spooler = value;
                OnPropertyChanged(nameof(Spooler));
            }
        }

        private string _Winder;
        public string Winder
        {
            get { return _Winder; }
            set
            {
                _Winder = value;
                OnPropertyChanged(nameof(Winder));
            }
        }

        private string _WinderSetPos;
        public string WinderSetPos
        {
            get { return _WinderSetPos; }
            set
            {
                _WinderSetPos = value;
                OnPropertyChanged(nameof(WinderSetPos));
            }
        }

        private string _WinderMove;
        public string WinderMove
        {
            get { return _WinderMove; }
            set
            {
                _WinderMove = value;
                OnPropertyChanged(nameof(WinderMove));
            }
        }

        #endregion

        #region Op Commands

        private string _OpMotion;
        public string OpMotion
        {
            get { return _OpMotion; }
            set
            {
                _OpMotion = value;
                OnPropertyChanged(nameof(OpMotion));
            }
        }

        private string _FRead;
        public string FRead
        {
            get { return _FRead; }
            set
            {
                _FRead = value;
                OnPropertyChanged(nameof(FRead));
            }
        }

        private string _OpPreset;
        public string OpPreset
        {
            get { return _OpPreset; }
            set
            {
                _OpPreset = value;
                OnPropertyChanged(nameof(OpPreset));
            }
        }

        #endregion

        #endregion

        #region Functions

        public CommandModel()
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
