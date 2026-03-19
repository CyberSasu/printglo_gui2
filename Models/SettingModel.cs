using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Net.WebSockets;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading.Tasks;
using System.Windows;
using static System.Runtime.InteropServices.JavaScript.JSType;

namespace Printgloo.Models
{
    public class SettingModel : INotifyPropertyChanged
    {
        #region Data Members

        public string FirmwareVersion { get; set; }

        private CommandModel _commands = new CommandModel();
        public CommandModel commands
        {
            get { return _commands; }
            set
            {
                if (_commands != value)
                {
                    _commands = value;
                    OnPropertyChanged(nameof(commands));
                }
            }
        }

        private ValueModel _values = new ValueModel();
        public ValueModel values
        {
            get { return _values; }
            set
            {
                if (_values != value)
                {
                    _values = value;
                    OnPropertyChanged(nameof(values));
                }
            }
        }

        #endregion

        #region initialization

        public SettingModel()
        {

        }

        public SettingModel ReadSettings()
        {
            try
            {
                JsonSerializerOptions options = new JsonSerializerOptions
                {
                    WriteIndented = true,
                    Converters = { new JsonStringEnumConverter() }
                };

                string filepath = (string)Application.Current.TryFindResource("FnameSettings");
                string jsonContent = File.ReadAllText(filepath);
                var s = JsonSerializer.Deserialize<SettingModel>(jsonContent, options);
                return s;
            }
            catch (Exception ex)
            {
                WriteSettings(new SettingModel());
                MessageBox.Show("Error with Settings! contact Freelancer");
                return new SettingModel();
            }
        }

        public void WriteSettings(SettingModel s)
        {
            JsonSerializerOptions options = new JsonSerializerOptions
            {
                WriteIndented = true,
                Converters = { new JsonStringEnumConverter() }
            };

            string filepath = (string)Application.Current.TryFindResource("FnameSettings");
            string jsonContent = JsonSerializer.Serialize(s, options);
            File.WriteAllText(filepath, jsonContent);
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
