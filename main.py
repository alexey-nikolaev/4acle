import kivy
kivy.require('1.9.1')

from datetime import datetime
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.carousel import Carousel
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.properties import ListProperty, StringProperty, NumericProperty, ObjectProperty, BooleanProperty
from kivy.lang import Builder
from random import choice
from kivy.clock import Clock
from kivy.base import EventLoop
from kivy.storage.jsonstore import JsonStore
from kivy.animation import Animation
from functools import partial
from kivy.utils import get_color_from_hex

from kivy.core.window import Window
Window.clearcolor = (1, 1, 1, 1)

skin = 0
colors = [['red', 'yellow', 'blue', 'green'], ['raspberry', 'deepblue', 'purple', 'aqua']] #circle, star, square, triangle
act_color, act_name, act_index_r, act_index_c = 'empty', 'empty', 0, 0
grid_gap = 0
score = 0
level = 0

def rules(action, state, act_color, act_index_r, act_index_c, end_color, end_index_r, end_index_c): #rules in form of [[targets rc]], [colors]
    if level == 0:
        if action == 'tap' and act_color == colors[skin][2]:
            return ([[end_index_r, end_index_c]], [colors[skin][3]])
        elif action == 'slide' and 0 < act_index_r < 3 and 0 < act_index_c < 3 and state[act_index_r+1][act_index_c+1] == colors[skin][2] and state[act_index_r-1][act_index_c-1] == colors[skin][2] and act_color == colors[skin][0]:
            return ([[end_index_r, end_index_c]], [colors[skin][1]])
        elif action == 'slide' and act_color == colors[skin][2] and end_color == colors[skin][3]:
            return ([[end_index_r, end_index_c]], [act_color])
        elif action == 'slide' and act_color == colors[skin][2] and end_color == colors[skin][1]:
            return ([[act_index_r, act_index_c], [end_index_r, end_index_c]], [colors[skin][0], colors[skin][0]])
        elif action == 'slide' and act_index_r < 3 and state[act_index_r+1][act_index_c] == colors[skin][2]:
            return ([[end_index_r, end_index_c]], [colors[skin][2]])
        else: return False
    if level == 1:
        if action == 'slide' and 0 < act_index_c < 3 and state[act_index_r][act_index_c+1] == colors[skin][3] and state[act_index_r][act_index_c-1] == colors[skin][3]:
            return ([[end_index_r, end_index_c]], [colors[skin][3]])
        elif action == 'slide' and act_index_r > 0 and state[act_index_r-1][act_index_c] == colors[skin][1]:
            return ([[end_index_r, end_index_c]], [colors[skin][0]])
        elif action == 'slide' and act_color == colors[skin][2] and end_color == colors[skin][0]:
            return ([[act_index_r, act_index_c], [end_index_r, end_index_c]], [end_color, act_color])
        elif action == 'slide' and act_color == colors[skin][0] and end_color == colors[skin][0]:
            return ([[act_index_r, act_index_c], [end_index_r, end_index_c]], [colors[skin][1], colors[skin][1]])
        else: return False

Builder.load_string('''
#: import sm1 kivy.uix.screenmanager

<Game>:

    orientation: 'vertical'
    
    ScreenManager:
        id: main_sm
        transition: sm1.RiseInTransition(duration = 0.1, clearcolor = [1,1,1,1])
        
        Screen:
            id: menu
            name: 'menu'
            
            MButton:
                id: new_game_btn
                text: 'new game'
                name: 'game'
                pos_hint: {'center_x': .5, 'center_y': .46}
                
            MButton:
                id: rules_btn
                text: 'rules'
                name: 'rules'
                pos_hint: {'center_x': .5, 'center_y': .34}

            MButton:
                id: highscore_btn
                text: 'highscore'
                name: 'highscore'
                pos_hint: {'center_x': .5, 'center_y': .22}
                
            MButton:
                id: settings_btn
                text: 'settings'
                name: 'settings'
                pos_hint: {'center_x': .5, 'center_y': .1}
                
            Logo:
                id: logo
                source: 'logo.png'
                allow_stretch: True
                size_hint: (0.8, 0.5)
                pos_hint: {'center_x': .5, 'center_y': .8}
                
        Screen:
            id: highscore
            name: 'highscore'
            
            Label:
                id: name
                text: 'name: ' + root.name
                pos_hint: {'center_x': .5, 'center_y': .55}
                color: [0, 0, 0, 1]
                
            Label:
                id: level
                text: 'level: ' + str(root.highscore)
                pos_hint: {'center_x': .5, 'center_y': .45}
                color: [0, 0, 0, 1]
                
        Screen:
            id: rules
            name: 'rules'
            
        SettingsScreen:
            id: settings
            name: 'settings'
            
            GridLayout:
                cols: 3
                spacing: '10dp'
                size_hint_y: None
                size_hint_x: .8
                height: self.minimum_height
                pos_hint: {'center_x': .5, 'center_y': .5}
                
                Label:
                    text: 'color scheme'
                    color: [0,0,0,1]
                    
                Option:
                    text: 'basic'
                    name: '0'
                    group: 'skin'
                    
                Option:
                    text: 'aqua'
                    name: '1'
                    group: 'skin'
                    
                Label:
                    text: 'sound'
                    color: [0,0,0,1]
                    
                Option:
                    text: 'on'
                    group: 'sound'
                    
                Option:
                    text: 'off'
                    group: 'sound'
                
        Screen:
            id: game
            name: 'game'

            BoxLayout:
                size_hint_y: None
                height: root.height*0.1
                pos: 0, root.top-self.height
                id: buttons
        
                Button:
                    id: play_btn
                    text: 'play'
                    background_color: (0.5, 0.5, 0.5, 1.0)
                    on_press: app.root.ids.sm.current = self.text
        
                Button:
                    id: test_btn
                    text: 'test'
                    background_color: (0.5, 0.5, 0.5, 1.0)
                    on_press: app.root.ids.sm.current = self.text
        
            ScreenManager:
                id: sm
                transition: sm1.SlideTransition(duration = 1)
                
                Screen:
                    id: screen1
                    name: 'play'
                    
                    Label:
                        id: score
                        text: 'score: ' + str(root.score)
                        color: [0, 0, 0, 1]
                        pos_hint: {'center_x': .2, 'center_y': .15}
                        
                    Label:
                        id: level
                        text: 'level: ' + str(root.level)
                        color: [0, 0, 0, 1]
                        pos_hint: {'center_x': .8, 'center_y': .15}
                        
                    Label:
                        id: play_mode
                        name: 'play_mode'
                        text: 'play mode'
                        markup: True
                        color: [0, 0, 0, 1]
                        pos_hint: {'center_x': .5, 'center_y': .85}
                    
                    Grid:
                        id: grid1
                        name: 'play_grid'
                        
                    Progress:
                        id: progress
        
                Screen:
                    id: screen2
                    name: 'test'
                    
                    Grid:
                        id: grid2
                        name: 'test_grid'
                        
                    Label:
                        id: test_mode
                        name: 'test_mode'
                        text: 'test mode'
                        markup: True
                        color: [0, 0, 0, 1]
                        pos_hint: {'center_x': .5, 'center_y': .85}
                        
                    Button:
                        id: reset
                        text: 'reset grid'
                        size_hint: (.8, .05)
                        pos_hint: {'center_x': .5, 'center_y': .15}
                        background_color: (0.5, 0.5, 0.5, 1.0)
                        on_press: app.root.ids.grid2.reset()
                        
                    Undo:
                        id: undo
                        source: 'undo.png'
                        size_hint: (.2, .2)
                        pos: (root.top, root.right)
                        allow_stretch: True
                        on_press: self.undo()
                        
            BoxLayout:
                size_hint_y: None
                height: root.height*0.1
                pos: 0, 0
                id: buttons2
        
                Button:
                    id: restart_btn
                    text: 'restart'
                    background_color: (0.5, 0.5, 0.5, 1.0)
                    on_press: root.restart()
        
                Button:
                    id: save_btn
                    text: 'save game'
                    background_color: (0.5, 0.5, 0.5, 1.0)
                    on_press: root.save_game()
                    
                Button:
                    id: load_btn
                    text: 'load game'
                    background_color: (0.5, 0.5, 0.5, 1.0)
                    on_press: root.load_game()

<Grid>:
    cols: 4
    rows: 4
    pos_hint: {'center_x': .5, 'center_y': .5}
    
    
<MButton>:
    background_color: (0.5, 0.5, 0.5, 1.0)
    size_hint: (0.8, 0.1)
    
''')

class Game(FloatLayout):
    storage = ObjectProperty()
    highscore = NumericProperty(0)
    name = StringProperty('')
    score = NumericProperty(0)
    level = NumericProperty(0)
        
    def restart(self, *args):
        def rebuild(*args):
            self.ids.progress.pos_hint_y = 1.
            self.ids.progress.text = ''
            popup.dismiss()
            self.ids.grid1.reset()
            self.ids.grid2.reset()
            self.level = 0
            self.score = 0
            global score
            score = 0
            global level
            level = 0
        def close(*args):
            popup.dismiss()
        layout = BoxLayout(orientation='vertical', spacing=10)
        layout.add_widget(Label(text='do you really want\nto restart the game?\n\nall unsaved progress\nwill be lost', halign='left', valign='middle', font_size='16sp'))
        buttons = BoxLayout(orientation='horizontal', size_hint_y=.1)
        buttons.add_widget(Button(text='yes', on_press=rebuild))
        buttons.add_widget(Button(text='no', on_press=close))
        layout.add_widget(buttons)
        popup = Popup(title='restart game', content=layout, separator_color=(1,1,1,1), separator_height='1dp', title_align='center', title_size='16sp', size_hint=(.85,.8), pos_hint = {'center_x': .5, 'center_y': .5}, auto_dismiss=False)
        popup.open()

    def save_game(self, *args):
        def set_name(*args):
            name = layout.children[2].text
            if name == '' or name == 'enter game name':
                return True
            else:
                popup.dismiss()
                self.ids.grid1.get_state()
                self.ids.grid2.get_state()
                timestamp = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M')
                self.storage.put(name, grid1 = self.ids.grid1.state, grid2 = self.ids.grid2.state, score = self.score, level = self.level, timestamp = timestamp)
        layout = BoxLayout(orientation="vertical")
        textinput = TextInput(text='enter game name', multiline=False, size_hint_y=.5)
        def clear(instance, value):
            if value: 
                if self.ids.progress.text == 'game over':
                    textinput.text = "can't save game over state"
                else: 
                    textinput.text = ''
        textinput.bind(focus=clear)
        layout.add_widget(textinput)
        layout.add_widget(Label(text='', size_hint_y=.1))
        buttons = BoxLayout(orientation='horizontal', size_hint_y=.5)
        popup = Popup(title='save game', content=layout, separator_color=(1,1,1,1), separator_height='1dp', title_align='center', title_size='16sp', size_hint=(.8, .22), pos_hint = {'center_x': .5, 'center_y': .7}, auto_dismiss=False)
        buttons.add_widget(Button(text='ok', on_press=set_name))
        buttons.add_widget(Button(text='cancel', on_press=popup.dismiss))
        layout.add_widget(buttons)
        popup.open()
        
    def load_game(self, *args):
        saves = []
        for key in self.storage.keys():
            if not key == 'highscore':
                saves.append(key)
        layout = BoxLayout(orientation="vertical", spacing=10)
        def show_prev(*args):
            carousel.load_previous()
        def show_next(*args):
            carousel.load_next()
        def start_loading(*args):
            self.ids.progress.pos_hint_y = 1.
            self.ids.progress.text = ''
            popup.dismiss()
            if not len(saves) == 0:
                selected = carousel.current_slide.children[2].text
                loaded = self.storage.get(selected)
                global level
                level = loaded['level']
                self.level = level
                global score
                score = loaded['score']
                self.score = score
                for i in range(4):
                    for j, color in enumerate(loaded['grid1'][i]):
                        self.ids.grid1.tiles[i][j].source = color + '.png'
                    for j, color in enumerate(loaded['grid2'][i]):
                        self.ids.grid2.tiles[i][j].source = color + '.png'
                if self.ids.grid1.tiles[0][0].source[:-4] not in colors[skin]:
                    self.ids.grid1.recolorize()
                    self.ids.grid2.recolorize()
                self.ids.grid1.get_state()
                self.ids.grid2.get_state()
        def delete(*args):
            if not len(saves) == 0:
                selected = carousel.current_slide.children[2].text
                self.storage.delete(selected)
                popup.dismiss()
                self.load_game()
        navigation = BoxLayout(orientation="horizontal", size_hint_y=.2)
        navigation.add_widget(Button(text='previous', on_press=show_prev))
        navigation.add_widget(Button(text='next', on_press=show_next))
        carousel = Carousel(direction='right')
        if len(saves) == 0:
            carousel.add_widget(Label(text='no saved games yet', font_size='16sp'))
        else:
            for name in saves:
                save_layout = BoxLayout(orientation='vertical')
                save_layout.add_widget(Label(text=''))
                save_layout.add_widget(Label(text=name, font_size='16sp'))
                save_layout.add_widget(Label(text=self.storage.get(name)['timestamp'], font_size='16sp'))
                save_layout.add_widget(Label(text=''))
                carousel.add_widget(save_layout)
        layout.add_widget(Label(text='choose saved game:', font_size='16sp'))
        layout.add_widget(Label(text=''))
        layout.add_widget(navigation)
        layout.add_widget(carousel)
        popup = Popup(title='load game', content=layout, separator_color=(1,1,1,1), separator_height='1dp', title_align='center', title_size='16sp', size_hint=(.85,.8), pos_hint = {'center_x': .5, 'center_y': .5}, auto_dismiss=False)
        buttons = BoxLayout(orientation='horizontal', size_hint_y=.2)
        buttons.add_widget(Button(text='load', on_press=start_loading))
        buttons.add_widget(Button(text='delete', on_press=delete))
        buttons.add_widget(Button(text='cancel', on_press=popup.dismiss))
        layout.add_widget(buttons)
        popup.open()
        
class MButton(Button):
    def __init__(self, **kwargs):
        super(MButton, self).__init__(**kwargs)
        pass
    
    def on_press(self, *args):
        self.parent.parent.current = self.name
        if self.text == 'new game': self.text = 'resume game'
        
class Option(ToggleButton):
    def __init__(self, **kwargs):
        super(Option, self).__init__(**kwargs)
        self.background_color = (0.5, 0.5, 0.5, 1)
        self.height = '48dp'
        self.size_hint_y = None
    
    def on_press(self, *args):
        if self.group == 'skin' and self.state == 'down':
            global skin
            skin = int(self.name)
            root = self.parent.parent.parent.parent
            root.ids.grid1.recolorize()
            root.ids.grid2.recolorize()
        if self.state == 'normal': self.state = 'down'
            
class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)
        
    def on_enter(self, *args):
        for elem in self.children[0].children:
            if hasattr(elem, 'group'):
                if elem.group == 'skin':
                    if elem.name == str(skin): elem.state = 'down'
                    else: elem.state = 'normal'
        
class Logo(Image):
    def __init__(self, **kwargs):
        super(Logo, self).__init__(**kwargs)
        self.bind(pos = self.set_size)
    
    def set_size(self, *args):
        self.width = self.parent.children[0].width
        self.height = self.width/1.411
        
class Undo(ButtonBehavior, Image):
    state_to_remember = ListProperty([])
    init_pos = ListProperty([])
    disabled = BooleanProperty(False)
    
    def undo(self, *args):
        if not self.disabled:
            for i in range(16):
                self.parent.children[3].tiles[i//4][i%4].source = self.state_to_remember[i//4][i%4] + '.png'
            self.parent.children[3].get_state()
            if not self.parent.children[3].tiles[0][0].source[:-4] in colors[skin]: self.parent.children[3].recolorize()
            self.disable()
        
    def disable(self, *args):
        self.pos =  (0 - self.width, 0 - self.height)
        self.disabled = True
        
    def enable(self, *args):
        self.pos = self.init_pos
        self.disabled = False
        
class Progress(Label):
    def __init__(self, **kwargs):
        super(Progress, self).__init__(**kwargs)
        self.size_hint = (.8, .2)
        self.position_hint = {'x':1, 'y':1}
        self.font_size = '48sp'
        self.color = get_color_from_hex('#FF00FF')
        self.text = ''
        self.halign = 'center'
        
    def animate(self, *args):
        anim = Animation(opacity=0., pos_hint = {'center_x':.5, 'center_y':1.2}, t='in_cubic', duration=1)
        anim.start(self)
        pass
    
    def put_in_place(self, *args):
        self.pos_hint = {'center_x':.5, 'center_y':.5}
        self.opacity = 1.
      
class Tile(Image):
    name = StringProperty('empty')
    index_r = NumericProperty(0)
    index_c = NumericProperty(0)
        
    def fall(self, depth):
        anim = Animation(x=self.x, y=self.y + grid_gap*depth, t='in_cubic', duration=0.5*(depth**0.5))
        anim.start(self)
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            global act_color 
            act_color = str(self.source)[:-4]
            global act_name
            act_name = self.name
            global act_index_r
            act_index_r = self.index_r
            global act_index_c
            act_index_c = self.index_c
            if touch.is_double_tap:
                action = 'tap'
                self.fire(action)
        
    def fire(self, action, *args):
        global grid_gap
        grid_gap = self.parent.tiles[1][0].y - self.parent.tiles[0][0].y
        if self.parent.name == 'test_grid':
            if len(self.parent.parent.children[0].init_pos) == 0:
                self.parent.parent.children[0].pos[0] = self.parent.center_x - 1.5*grid_gap
                self.parent.parent.children[0].init_pos.append(self.parent.center_x - 1.5*grid_gap)
                self.parent.parent.children[0].pos[1] = self.parent.center_y - 1.5*grid_gap
                self.parent.parent.children[0].init_pos.append(self.parent.center_y - 1.5*grid_gap)
            self.parent.parent.children[0].state_to_remember = self.parent.state
            self.parent.parent.children[0].enable()
        root = self.parent.parent.parent.parent.parent
        self.parent.get_state()
        response = rules(action, self.parent.state, act_color, act_index_r, 
                 act_index_c, str(self.source)[:-4], self.index_r, self.index_c)
        if response:
            for i, color in zip(response[0], response[1]):
                self.parent.tiles[i[0]][i[1]].source = color + '.png'
            self.parent.get_state()
            res = self.parent.check()
            if not len(res[0])+len(res[1])==0: self.parent.explode()
            else: self.parent.check_moves()
        elif self.parent.name == 'play_grid': 
            root.parent.score -= 1
            global score
            score = root.parent.score
            if score <= -3: self.parent.finalize('game over')
            
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos) and not self.name == act_name:
            if abs(self.index_r-act_index_r)+abs(self.index_c-act_index_c) == 1:
                action = 'slide'
                self.fire(action)
            
class Grid(GridLayout):
    state = ListProperty([])
    tiles = ListProperty([])
    
    def __init__(self, **kwargs):
        super(Grid, self).__init__(**kwargs)
        self.size_hint_x = .8
        self.bind(height = self.set_height)
        for i in range(16):
            self.add_widget(Tile(name='tile'+str(i), index_r=i//4, index_c=i%4,
                                 source=choice(colors[skin])+'.png', allow_stretch=True))
        t = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        for tile in self.children:
            for i in range(16):
                if tile.index_r == i//4 and tile.index_c == i%4:
                    t[i//4][i%4] = tile
                    break
        self.tiles = t
        self.get_state()
        self.check_init()
        
    def check_init(self, *args):
        c_list = []
        for i in range(4):
            c_list += self.state[i]
        for color in colors[skin]:
            if c_list.count(color) < 3: self.reset()
        res = self.check()
        if not len(res[0])+len(res[1]) == 0: self.reset()
          
    def reset(self, *args):
        self.clear_widgets()
        self.__init__()
        
    def finalize(self, mode, *args):
        root = self.parent.parent.parent.parent.parent
        if level > root.highscore:
            def set_name(*args):
                name = layout.children[1].text
                if name == '' or name == 'enter your name':
                    return True
                else:
                    popup.dismiss()
                    root.storage.put('highscore', level = level, name = name)
                    root.highscore = level
                    root.name = name
            layout = BoxLayout(orientation="vertical", spacing=10)
            textinput = TextInput(text='enter your name', multiline=False)
            def clear(instance, value):
                if value: textinput.text = ''
            textinput.bind(focus=clear)
            layout.add_widget(textinput)
            layout.add_widget(Button(text='ok', on_press=set_name))
            popup = Popup(title='new highscore', content=layout, separator_color=(1,1,1,1), separator_height='1dp', title_align='center', title_size='16sp', size_hint=(.8, .22), pos_hint = {'center_x': .5, 'center_y': .7}, auto_dismiss=False)
            popup.open()
        progress = root.ids.progress
        progress.text = mode
        progress.put_in_place()
        
    def check(self, *args):
        r_targets = []
        c_targets = []
        for i in range(4):
            if len(set(self.state[i])) == 1:
                r_targets.append(i)
            if len(set([self.state[0][i], self.state[1][i], self.state[2][i], self.state[3][i]])) == 1:
                c_targets.append(i)
        return [r_targets, c_targets]
    
    def aftercheck(self, *args):
        self.get_state()
        res = self.check()
        if not len(res[0])+len(res[1])==0: self.explode()
        else: 
            self.check_moves()
            if self.name == 'test_grid': self.parent.children[0].enable()
        
    def explode(self, *args):
        root = self.parent.parent.parent.parent.parent
        res = self.check()
        hit = len(res[0])+len(res[1])
        if self.name == 'play_grid':
            progress = root.ids.progress
            progress.text = '+'+str(int(hit*0.5*(hit+1)))
            progress.put_in_place()
            progress.animate()
            root.score += int(hit*0.5*(hit+1))
            if root.score >= 10: 
                root.level += 1
                progress = root.ids.progress
                progress.text = 'level up'
                progress.put_in_place()
                progress.animate()
                def turn_screens(*args):
                    root.ids.sm.current = 'test'
                Clock.schedule_once(turn_screens, 1)
                root.score -= 10
            global score
            score = root.score
            global level
            level = root.level
            if level > 1: self.finalize('you win')
                
        for target in res[0]:
            for i in range(4):
                self.tiles[target][i].y = 0 - self.tiles[target][i].height
        for target in res[1]:
            for i in range(4):
                self.tiles[i][target].source = ''
        Clock.schedule_once(partial(self.update_grid, res), 0.5)
        
    def check_moves(self, *args):
        root = self.parent.parent.parent.parent.parent
        def no_more_moves(*args):
            flag0 = False
            flag1 = False
            state = self.state
            for i in range(4):
                if flag0: break
                for j in range(4):
                    if flag1: 
                        flag0 = True
                        break
                    act_color = self.state[i][j]
                    act_index_r, act_index_c = i, j
                    if rules('tap', state, act_color, act_index_r, act_index_c, act_color, act_index_r, act_index_c):
                        flag0 = True
                        break
                    cl = [] #checklist
                    if i>0: cl.append([i-1, j])
                    if j>0: cl.append([i, j-1])
                    if i<3: cl.append([i+1, j])
                    if j<3: cl.append([i, j+1])
                    for elem in cl:
                        if rules('slide', state, act_color, act_index_r, act_index_c, state[elem[0]][elem[1]], elem[0], elem[1]): 
                            flag1 = True
                            return False
                            break
            else: return True
        if no_more_moves():
            if self.name == 'play_grid':
                root.ids.progress.text = 'no more moves\n-3'
            else:
                root.ids.progress.text = 'no more moves'
            root.ids.progress.put_in_place()
            root.ids.progress.animate()
            if self.name == 'play_grid':
                global score
                score -= 3
                root.score = score
                if score <= -3: Clock.schedule_once(partial(self.finalize, 'game over'), 2)
                else: self.reset()
                    
    def update_grid(self, res, dt):
        if self.name == 'test_grid':
            self.parent.children[0].disable()
        if not len(res[0]) == 0:
            row = min(res[0])-1
            depth = len(res[0])
            while row > -1:
                for i in range(4):
                    self.tiles[row][i].fall(depth)
                row -= 1
            for target in res[0]:
                for i in range(4):
                    self.tiles[target][i].source = choice(colors[skin])+'.png'
            d = self.tiles
            a = min(res[0])
            b = max(res[0])
            self.tiles = d[a:b+1]+d[:a]+d[b+1:]
            for i in range(4):
                for j in range(4):
                    self.tiles[i][j].index_r = i
            if min(res[0]) == 0:
                if not len(res[1]) == 0:
                    Clock.schedule_once(partial(self.show_rows, len(res[0])), 0.2+0.25*4)
                else: 
                    Clock.schedule_once(partial(self.show_rows, len(res[0])), 0.2)
            else:
                if not len(res[1]) == 0:
                    Clock.schedule_once(partial(self.show_rows, len(res[0])), 0.2+0.5*(depth**0.5)+0.25*(4-(depth-1)))
                else:
                    Clock.schedule_once(partial(self.show_rows, len(res[0])), 0.2+0.5*(depth**0.5))
            self.get_state()
                
        if not len(res[1]) == 0:
            if not len(res[0]) == 0:
                if min(res[0]) == 0:
                    Clock.schedule_once(partial(self.show_columns, res[1]), 0.2)
                else:
                    Clock.schedule_once(partial(self.show_columns, res[1]), 0.2+0.5*(depth**0.5))
            else:
                Clock.schedule_once(partial(self.show_columns, res[1]), 0.2)
            self.get_state()
                
    def show_rows(self, depth, dt):
        for i in range(depth):
            for j in range(4):
                Clock.schedule_once(partial(self.show_tile, 'r', i, j), 0.25*(depth-i-1)+j*0.25)
        Clock.schedule_once(self.aftercheck, 2.5)
                
    def show_columns(self, c_targets, dt):
        for i in range(4):
            for target in c_targets:
                Clock.schedule_once(partial(self.show_tile, 'c', i, target), 0.25*(4-i))
        Clock.schedule_once(self.aftercheck, 2.5)
    
    def show_tile(self, mode, index_r, index_c, dt):
        if mode == 'c':
            self.tiles[index_r][index_c].source = choice(colors[skin])+'.png'
        if mode == 'r':
            self.tiles[index_r][index_c].center_y = self.center_y - (1.5-index_r)*grid_gap
        
    def set_height(self, *args):
        if self.width >= 0.5*self.parent.height: self.width = 0.5*self.parent.height
        self.height = self.width
        
    def get_state(self, *args):
        s = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        for i in range(16):
            s[i//4][i%4] = self.tiles[i//4][i%4].source[:-4]
        self.state = s
        
    def recolorize(self, *args):
        c = 0
        while self.tiles[0][0].source[:-4] not in colors[c]:
            c += 1
        for i in range(16):
            for j in range(4):
                if self.tiles[i//4][i%4].source[:-4] == colors[c][j]:
                    self.tiles[i//4][i%4].source = colors[skin][j] + '.png'
                    break
        self.get_state()
                
class fouracleApp(App):
    game = ObjectProperty()
    
    def build(self):
        storage = JsonStore('storage_file.json')
        try: 
            storage.get('highscore')
        except KeyError:
            storage.put('highscore', level = 0, name = 'no highscores yet')
        game = Game()
        game.storage = storage
        game.highscore = storage.get('highscore')['level']
        game.name = storage.get('highscore')['name']
        self.game = game
        return game
        
    def on_start(self, *args):
        EventLoop.window.bind(on_keyboard=self.hook_keyboard)

    def hook_keyboard(self, window, key, *args):
        if key == 27:
           self.game.ids.main_sm.current = 'menu'
           return True 
        
if __name__ == '__main__':
    fouracleApp().run()
