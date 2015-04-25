using System.ComponentModel;

namespace MineSweeping.Model
{
    public class GameSetting : INotifyPropertyChanged
    {
        public GameSetting(int width,int height)
        {
            _width = width;
            _height = height;
            _canMarkCount = width*height;
        }

        private int _height;
        public int Height
        {
            get { return _height; }
            set
            {
                _height = value;
                OnPropertyChanged("Height");
            }
        }

        private int _width;
        public int Width
        {
            get { return _width; }
            set
            {
                _width = value;
                OnPropertyChanged("Width");
            }
        }

        private int _canMarkCount;
        public int CanMarkCount
        {
            get { return _canMarkCount; }
            set
            {
                _canMarkCount = value;
                OnPropertyChanged("CanMarkCount");
            }
        }

        private int _useSecond;
        public int UseSecond
        {
            get { return _useSecond; }
            set
            {
                _useSecond = value;
                OnPropertyChanged("UseSecond");
            }
        }

        public event PropertyChangedEventHandler PropertyChanged;

        private void OnPropertyChanged(string property)
        {
            if (PropertyChanged != null)
            {
                PropertyChanged(this, new PropertyChangedEventArgs(property));
            }
        }
    }
}