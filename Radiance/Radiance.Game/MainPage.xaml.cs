using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Animation;
using System.Windows.Shapes;
using System.Xml.Linq;
using Radiance.Core.AStar;
using Radiance.Game.Common;
using Radiance.Game.Enumeration;
using Radiance.Game.Model;
using Radiance.Game.Objects;
using Radiance.Game.Resolver;


namespace Radiance.Game
{
    public partial class MainPage : UserControl
    {
        private byte[,] _fixedRoadblock;

        public MainPage()
        {
            InitializeComponent();
            SetGameCursor(0);

            _gridsizeX = 10;
            _gridsizeY = 10;
            
            LoadMap();
            LoadRoadBlock();
            map.FixedRoadBlock = _fixedRoadblock;
        }

        private int _gridsizeX, _gridsizeY;
        private int GetMatrixSize(int n)
        {
            if (n <= 1280)
            {
                return 128;
            }
            if (1280 < n && n <= 2560)
            {
                return 256;
            }
            if (2560 < n && n <= 5120)
            {
                return 512;
            }
            if (5120 < n && n <= 10240)
            {
                return 1024;
            }
            return 10240 < n && n <= 20480 ? 2048 : 10240;
        }
        private void LoadRoadBlock()
        {
            XElement mapElement = XElement.Load("Config/Roadblock/0.xml");
            int size = map.FullWidth > map.FullHeight ? GetMatrixSize(map.FullWidth) : GetMatrixSize(map.FullHeight);
            _fixedRoadblock = new byte[size, size];
            for (int y = 0; y < _fixedRoadblock.GetUpperBound(1); y++)
            {
                for (int x = 0; x < _fixedRoadblock.GetUpperBound(0); x++)
                {
                    //设置默认值,可以通过的均在矩阵中用1表示
                    _fixedRoadblock[x, y] = 1;
                }
            }
            //设置初始值,可以通过的均在矩阵中用1表示
            string[] obstruction = mapElement.Attribute("Value").Value.Split(',');
            for (int i = 0; i < obstruction.Count(); i++)
            {
                string[] obstructionXY = obstruction[i].Split('_');
                int xpoint = Convert.ToInt32(obstructionXY[0]);
                int ypoint = Convert.ToInt32(obstructionXY[1]);
                _fixedRoadblock[xpoint,ypoint ] = 0;

                //Rectangle rectangle = new Rectangle() { Width = 10, Height = 10 };
                //rectangle.Fill = new SolidColorBrush(Colors.Yellow);
                //rectangle.SetValue(Canvas.LeftProperty, (double)xpoint * _gridsizeX);
                //rectangle.SetValue(Canvas.TopProperty, (double)ypoint * _gridsizeY);
                //map.Children.Add(rectangle);
            }
        }

        private Map map;
        private void LoadMap()
        {
            map = new Map(0, 2400, 2400, 400, 300, Root.Width, Root.Height, Carrier);
            map.GridSize = 10;
            LoadLeader(500, 230);
            map.Leader = Leader;

            Effect effect = new Effect(new FrameResolver(), new ObjectPart(ObjectPartType.Effect, 2), Actions.Stand,
                                       new ActionState(9, 100), new Size(300, 300)) {CoordinateMarginTop = 190};
            effect.RepeatCount = 1;
            effect.AttachObject = Leader;
            map.AddObject(effect);

            LoadMonster(100, new Point(300, 300),5,5,6);
            LoadMonster(200,new Point(350,400),4,6,8);

            LoadNpc(0,2,new Point(270,200),"血染尘" );
            LoadNpc(1,1,new Point(600,300),"西部牛仔" );
        }

        private void LoadNpc(int spriteCode,int weaponCode,Point coordinate,string name)
        {
            NPC npc = new NPC(new XYQRoleFrameResolver(), new List<ObjectPart>()
                                                              {
                                                                  new ObjectPart(ObjectPartType.Body, spriteCode),
                                                                  new ObjectPart(ObjectPartType.Weapon, weaponCode)
                                                              }, new Dictionary<Actions, ActionState>()
                                                                     {
                                                                         {Actions.Stand, new ActionState(9, 400)},
                                                                         {Actions.Run, new ActionState(8, 100)}
                                                                     }, new Size(250, 250), new Rect(97, 80, 60, 90));
            npc.CoordinateMarginTop = 195;
            npc.CoordinateMarginLeft = 155;
            npc.CharacterName = name;
            npc.Coordinate = coordinate;
            map.AddObject(npc);
        }

        private void LoadMonster(int spriteCode,Point coordinate,int runFrame,int deathFrame,int attackFrame)
        {
            var objectParts = new List<ObjectPart>();
            objectParts.Add(new ObjectPart(ObjectPartType.Body, spriteCode, new Point(0, 0)));
            Dictionary<Actions, ActionState> actionStates = new Dictionary<Actions, ActionState>()
                                                                   {
                                                                       {Actions.Stand,new ActionState(5,400)},
                                                                       {Actions.Run,new ActionState(runFrame,150)},
                                                                       {Actions.Death,new ActionState(deathFrame,200)},
                                                                       {Actions.Attack,new ActionState(attackFrame,150)}
                                                                   };
            Monster monster = new Monster(new JianXiaFrameResolver(), objectParts, actionStates, new Size(320, 320), new Rect(120, 90, 110, 140));
            monster.IsActiveAttack = true;
            monster.AttackRange = 80;
            monster.SeekRange = 200;
            monster.LifeUITotalWidth = 80;
            monster.FullLife = 100;
            monster.Life = 100;
            monster.CoordinateMarginLeft = 160;
            monster.CoordinateMarginTop = 215;
            monster.Coordinate = coordinate;
            map.AddObject(monster);
        }

        Leader Leader;
        /// <summary>
        /// 加载主角
        /// </summary>
        private void LoadLeader(double x, double y)
        {
            var objectParts = new List<ObjectPart>();
            objectParts.Add(new ObjectPart(ObjectPartType.Head, 1001));
            objectParts.Add(new ObjectPart(ObjectPartType.LeftArm, 1001));
            objectParts.Add(new ObjectPart(ObjectPartType.RightArm, 1001));
            objectParts.Add(new ObjectPart(ObjectPartType.Body, 1001));
            objectParts.Add(new ObjectPart(ObjectPartType.LeftHand,1001));
            objectParts.Add(new ObjectPart(ObjectPartType.Weapon, 1001));

            Dictionary<Actions, ActionState> actionStates = new Dictionary<Actions, ActionState>()
                                                                   {
                                                                       {Actions.Stand,new ActionState(5,400)},
                                                                       {Actions.Run,new ActionState(8,100)},
                                                                       {Actions.Attack,new ActionState(7,200)},
                                                                       {Actions.Magic,new ActionState(7,200)}
                                                                   };
            Leader = new Leader(new JianxiaLeaderFrameResolver(), objectParts, actionStates, new Size(320, 320), new Rect(140, 120, 44, 108));
            LoadSprite(
                    Leader,
                    "大荒先行义士",
                    "坎普利特",
                    160,
                    210,
                    new Point(x, y)
                );
           
        }

        private void LoadSprite(Sprite sprite, string title, string name, double centerX, double centerY, Point coordinate)
        {
            sprite.Title = title;
            sprite.CharacterName = name;
            sprite.HoldGridX = 2;
            sprite.HoldGridY = 1;
            sprite.CoordinateMarginLeft = centerX;
            sprite.CoordinateMarginTop = centerY;
            sprite.Coordinate = coordinate;
            sprite.FullLife = 1000;
            sprite.Life = 1000;
            sprite.AttackRange = 70;
        }

        #region 游戏相关事件

        private void Game_MouseLeftButtonDown(object sender, MouseButtonEventArgs e)
        {
            Leader.LockSprite = FindHitSprite();
            Point position = e.GetPosition(map);
            Leader.MoveTo(position);
        }

        //鼠标移动(悬停)事件
        private void Game_MouseMove(object sender, MouseEventArgs e)
        {
            this.Dispatcher.BeginInvoke(() => ChangeCursor(e));
        }

        private void ChangeCursor(MouseEventArgs e)
        {
            Point position = e.GetPosition(Root);
            GameCursor.SetValue(Canvas.LeftProperty, position.X); GameCursor.SetValue(Canvas.TopProperty, position.Y);

            //去除发光效果
            if (_hitSprite != null)
            {
                _hitSprite.ShadowVisible = false;
            }

            HitSprite(position,e);
            if(_hitSprite!=null)
            {
                _hitSprite.ShadowVisible = true;
            }
            SetGameCursor(_hitSprite!=null ? 1 : 0);
        }

        private int _currentCursorCode = -1;
        private void SetGameCursor(int cursorCode)
        {
            if (_currentCursorCode == cursorCode)
            {
                return;
            }
            GameCursor.Source = ImageUtils.GetRelativeImage("/Radiance.Game;component/Resources/Cursor/" + cursorCode.ToString() + ".png", true);
            _currentCursorCode = cursorCode;
        }

        private Sprite FindHitSprite()
        {
            return _hitSprite;
        }

        private Sprite _hitSprite;
        /// <summary>
        /// 获取鼠标下的精灵
        /// </summary>
        private void HitSprite(Point position,MouseEventArgs e)
        {
            List<UIElement> hitElements = VisualTreeHelper.FindElementsInHostCoordinates(position, Carrier) as List<UIElement>;
            _hitSprite =
                hitElements.OfType<Sprite>().FirstOrDefault(
                    s => s != Leader && CollisionDetectionUtils.IsInRect(s.PhysicalArea, e.GetPosition(s)));
        }

        #endregion

    }
}
