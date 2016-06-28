'''
 _______  __   __  __   __  _______  ___      _______  ___      _______ 
|       ||  | |  ||  |_|  ||       ||   |    |       ||   |    |  _    |
|    _  ||  |_|  ||       ||   _   ||   |    |___    ||   |___ | | |   |
|   |_| ||       ||       ||  | |  ||   |     ___|   ||    _  || | |   |
|    ___||_     _||       ||  |_|  ||   |___ |___    ||   | | || |_|   |
|   |      |   |  | ||_|| ||       ||       | ___|   ||   |_| ||       |
|___|      |___|  |_|   |_||_______||_______||_______||_______||_______|
'''


'''

PYMOL360: Platform for Multiuser Gamepad Support with PyMOL

This script was designed to adapt real-time visualization of PyMOL to a multiuser environment
Particular emphasis was placed in making the usage of the program simple and flexible so it can hopefully find
some use in educational setttings in addition to professional presentation and discussion.


If you have comments, questions, or want to talk about something interesting, please contact:

Patrick V. Holec
hole0077@umn.edu
(612)868-9858
University of Minnesota
'''


'''
NOTE FOR ADDING COMMANDS:
We acknowledge PyMOL has tons of visualization features, and including options for all of them can be very impractical.
Therefore, we have a modular system for adding controls so you can make special functions without too much fuss! There are two steps:

1. Go to the PyMOL_Command function in the PyMOL class and add a new elif command == '<insert command shortcut name>'
   The code inside the function will execute whenever the key bound to the command shortcut name is pressed.

2. Go to __init__ function of the Controls class. Add your command shortcut name to the list of controls (self.options)

Next time you start up PYMOL360, your newly created control should be there in the listing. Bind it to whatever key you want!
'''


'''
You might think: "But there's just too many that I want to modify to get a good picture of what I want to show..."

Not a problem!

If you format a structure prior to starting PYMOL360, it will stay open (if the structure is active in the submenu)!
Then, you can also save the setting to a profile so next time you want to show off your structure, everythings ready to roll.
'''


'''
SECTION: Initialization
PURPOSE: Import all necessary modules and declare some baseline variables
NOTE: Pygame is the only module not already installed to PyMOL and it has some permission problems, so you will need to do this manually.
      Attempts to make this occur automatically were tried but none were able to do this seamlessly.
'''

run = True

try:
    import pygame
except:
    print 'Pygame module not found in PyMOL Python instance. Please see README.txt for instructions on installation.'
    run = False
    
import sys
import glob,os,shelve
import urllib2
import pickle
import copy

from pymol import cmd,stored   # This is the module that controls PyMOL interactions

# Define some colors
BLACK    = (   80,   80,   80)
WHITE    = ( 255, 255, 255)

# This is a simple class that will help us print to the screen
# It has nothing to do with the joysticks, just outputing the
# information.

### Here are some global variables that you can change if you prefer
global sensitivity
# Sensitivity of rotation
sensitivity = 5.

'''
SECTION: Map String Activation to Functions
PURPOSE: This function converts interpretor functions to commands in PyMOL
NOTE: Functions here are modular, so you can theoretically create new function combinations as desired
'''
def Color_Refresh(colors,i,selection='all'):
    cmd.color(colors[i%len(colors)],selection)

def Show_Refresh(shows,i,i2,selection='all'):
    cmd.hide(shows[i2%len(shows)],selection)
    cmd.show(shows[i%len(shows)],selection)

def Structure_Refresh(actives,i):
    cmd.disable('all')
    cmd.enable(actives[i%len(actives)])
    cmd.orient(actives[i%len(actives)])

# Little function for downloading PDBs if there are none in the folder
def Fetch_PDB(id):
    url = 'http://www.rcsb.org/pdb/files/%s.pdb' % id
    response = urllib2.urlopen(url)
    f = open(id + '.pdb', 'w')
    f.write(response.read())
    f.close()

# This function checks for any preloaded structures, and if they do exist, moves them to the PyMOL360 directory
def Preloaded_Structures():
    names = cmd.get_names('objects')
    for name in names:
        if not(os.path.isfile(name+'.pdb')):
            print 'Moving file to PyMOL360 directory: ' + name + '.pdb'
            cmd.save(name+'.pdb',selection = name)
    return names

'''
SECTION: PyMOL Class
PURPOSE: All controls to the main PyMOL interface
NOTE: This is the only class that directly interacts with PyMOL
IMPORTANT VARIABLES:
self.active - list of structure strings
self.active_state - index of the active structure
self.seqs - list of lists of tuples, each residue/index for each active structure
'''
class PyMOL:
    def __init__(self):
        # This is a placeholder if there ever needs to be some pre-initialized stuff
        pass

    # Figure out what's already loaded so we dont cover up existing structures
    def Menu(self,options,states,advanced,actives,filename=False):
        if len(actives) == 0:
            print 'No active structures... please activate atleast one structure.'
        else:
            cmd.set('seq_view',0)
            cmd.disable('all')
            structures = cmd.get_object_list('all') # Figure out what's already loaded so we dont cover up existing structures
            self.seqs = []            
            for active in actives:  # Iterate through all active PDBs (dictated by menu)
                if not active in structures: # If its not already loaded...
                    print 'Loading %s ...' % active
                    try:
                        os.chdir(directory)
                        cmd.load(active+'.pdb')  # Load it!
                        time.sleep(0.5)
                    except:  # If its not there...
                        print 'Not located locally, fetching file...'
                        cmd.fetch(active)  # Fetch it!
                residues = {'my_list' : []}
                cmd.iterate('(name ca) and '+active,"my_list.append((resi,resn))",space=residues)
                self.seqs.append([('all','(none)')]+residues['my_list'])
                cmd.refresh()

            # Random value declarations
            self.zoom,self.lock = 1.,0
            self.active_state,self.color_state,self.show_state = 0,0,0
            self.active = actives

            self.index = [0 for i in actives]   # This is for tracking the residue number
            self.color = [i for i,j in zip(advanced.colors[0],advanced.colors[1]) if j == 1]
            self.show = [i for i,j in zip(advanced.show[0],advanced.show[1]) if j == 1]
            if filename:
                cmd.load(filename+'.pse')
                profiles.kickstarter = False
            else:
                if profiles.kickstarter: # If a new profile is loaded, it'll overwrite the current scene with the saved session
                    print 'Loading saved scene from %s' % profiles.profiles[profiles.states.index(1)]
                    try:
                        cmd.load(profiles.profiles[profiles.states.index(1)]+'.pse')
                        profiles.kickstarter = False
                    except:
                        print 'No scene detected.'
                    cmd.refresh()

            self.window = Window([400,200],title='PyMOL360 Mode')  # Creates a mini-window for a HUD!
            
            cmd.disable('all')
            Structure_Refresh(self.active,self.active_state)
            cmd.zoom(self.active[self.active_state],self.zoom)
            self.Interpreter(options,states)

    # This lovely function maps any activated commands to actual functions in PyMOL
    # Both inputs (commands and amps) are lists to be iterated simultaneously.
    # Commands are string labels, amps are amplitudes ( in case of gradient controls like joysticks )
    def PyMOL_Command(self,commands,amps):
        for command,amp in zip(commands,amps):
            if command == 'Rotate (X)':
                if self.lock == 0:
                    cmd.turn('x',sensitivity*amp)
                else:
                    cmd.translate([0,-sensitivity*amp/2,0])
            
            elif command == 'Rotate (Y)':
                if self.lock == 0:
                    cmd.turn('y',sensitivity*amp)
                else:
                    cmd.translate([sensitivity*amp/2,0,0])
                    
            elif command == 'Rotate (Z)':
                if self.lock == 0:
                    cmd.turn('z',sensitivity*amp)
                else:
                    pass
                
            elif command == 'Escape':
                print 'Leaving environment...'
                return True
                
            elif command == 'Cycle Structures (forward)':
                self.active_state -= 1
                self.active_state = self.active_state%len(self.active)
                Structure_Refresh(self.active,self.active_state)
                self.PyMOL_Update()
                
            elif command == 'Cycle Structures (backward)':
                self.active_state += 1
                self.active_state = self.active_state%len(self.active)
                Structure_Refresh(self.active,self.active_state)
                self.PyMOL_Update()
                
            elif command == 'Cycle display (forward)':
                self.show_state -= 1
                if self.seqs[self.active_state][self.index[self.active_state]][0] != 'all':
                    select = self.active[self.active_state]+' and resi '+self.seqs[self.active_state][self.index[self.active_state]][0]
                else:
                    select = self.active[self.active_state]
                Show_Refresh(self.show,self.show_state,self.show_state+1,select)
                self.PyMOL_Update()
                
            elif command == 'Cycle display (backward)':
                self.show_state += 1
                if self.seqs[self.active_state][self.index[self.active_state]][0] != 'all':
                    select = self.active[self.active_state]+' and resi '+self.seqs[self.active_state][self.index[self.active_state]][0]
                else:
                    select = self.active[self.active_state]
                Show_Refresh(self.show,self.show_state,self.show_state-1,select)
                self.PyMOL_Update()
                
            elif command == 'Cycle colors (forward)':
                self.color_state -= 1
                if self.seqs[self.active_state][self.index[self.active_state]][0] != 'all':
                    select = self.active[self.active_state]+' and resi '+self.seqs[self.active_state][self.index[self.active_state]][0]
                else:
                    select = self.active[self.active_state]
                Color_Refresh(self.color,self.color_state,select)
                self.PyMOL_Update()
                
            elif command == 'Cycle colors (backward)':
                self.color_state += 1
                if self.seqs[self.active_state][self.index[self.active_state]][0] != 'all':
                    select = self.active[self.active_state]+' and resi '+self.seqs[self.active_state][self.index[self.active_state]][0]
                else:
                    select = self.active[self.active_state]
                Color_Refresh(self.color,self.color_state,select)
                self.PyMOL_Update()
                
            elif command == 'Zoom (forward)':
                if self.seqs[self.active_state][self.index[self.active_state]][0] != 'all':
                    select = self.active[self.active_state]+' and resi '+self.seqs[self.active_state][self.index[self.active_state]][0]
                else:
                    select = self.active[self.active_state]
                self.zoom += 0.2*amp
                cmd.zoom(select,self.zoom)

            elif command == 'Zoom (backward)':
                if self.seqs[self.active_state][self.index[self.active_state]][0] != 'all':
                    select = self.active[self.active_state]+' and resi '+self.seqs[self.active_state][self.index[self.active_state]][0]
                else:
                    select = self.active[self.active_state]
                self.zoom -= 0.2*amp
                cmd.zoom(select,self.zoom)

            elif command == 'Screen Lock':
                self.lock = 1 - self.lock

            elif command == 'Reset Molecule':
                cmd.delete(self.active[self.active_state])
                cmd.load(self.active[self.active_state]+'.pdb')
                cmd.enable(self.active[self.active_state])

            elif command == 'Reset View':
                cmd.orient(self.active[self.active_state])

            elif command == 'Orient':
                if self.seqs[self.active_state][self.index[self.active_state]][0] != 'all':
                    select = self.active[self.active_state]+' and resi '+self.seqs[self.active_state][self.index[self.active_state]][0]
                    self.zoom = 1.  # Reset zoom for continuity issues
                else:
                    select = self.active[self.active_state]
                cmd.orient(select)
                cmd.zoom(select,self.zoom)

            elif command == 'Iterate Residue (forward)':
                self.index[self.active_state] += 1
                self.index[self.active_state] = self.index[self.active_state]%len(self.seqs[self.active_state])        
                cmd.delete('sele')
                if self.seqs[self.active_state][self.index[self.active_state]][0] != 'all':
                    cmd.select(self.active[self.active_state]+' and resi '+self.seqs[self.active_state][self.index[self.active_state]][0])
                self.PyMOL_Update()

            elif command == 'Iterate Residue (backward)':
                self.index[self.active_state] -= 1
                self.index[self.active_state] = self.index[self.active_state]%len(self.seqs[self.active_state])
                cmd.delete('sele')
                if self.seqs[self.active_state][self.index[self.active_state]] != 'all':
                    cmd.select(self.active[self.active_state]+' and resi '+self.seqs[self.active_state][self.index[self.active_state]][0])
                self.PyMOL_Update()                 
                
        return False

    # This function interprets key presses from the user and converts them to commands for PyMOL execution
    # The done variable is used to manage whether it wants to quit such as if an escape button is pressed
    def Interpreter(self,controls,controls_map):
        controls2,controls2_map = controls[:],controls_map[:]
        '''
        Two types of controls exist:
            + Updaters: these must check state on each iteration to allow scrolling features for the viewer
                        having all variables as these updaters significantly slows the speed of the function so we reserve
                        this for only controls that particularly benefit from this type of processing
            + Controls: toggleable, detected on an event for which the button is pressed. It will then be mapped to its control
        '''

        # Figuring out which binds are controls or updaters
        updaters = ['Rotate (X)','Rotate (Y)','Rotate (Z)','Zoom (forward)'] # These are the updaters
        updaters_map = [controls2_map[controls2.index(i)] for i in updaters]
        updaters = [updaters[i] for i,update in enumerate(updaters_map)]
        updaters_map = filter(None, updaters_map)

        for i in updaters:
            controls2_map.pop(controls2.index(i))
            controls2.pop(controls2.index(i))


        # Hastily adding functionality for displaying controls on HUD
        self.updaters,self.updaters_map = updaters,updaters_map
        self.controls2,self.controls2_map = controls2,controls2_map

        self.PyMOL_Update()
        
        done = False
        
        while done == False:
            time.sleep(0.02)
            ID,amp = [],[]
            for js in window.joystick:  # Check for updaters state on each controller
                for i,update in enumerate(updaters_map):
                    if update[0:4] == 'Axis':
                        temp = js.get_axis(int(update[5:]))**3
                        if abs(temp) > 0.001:
                            ID.append(updaters[i])
                            amp.append(temp)
                    elif update[0:6] == 'Button':
                        temp = js.get_button(int(update[7:]))
                        if temp > 0.1:
                            ID.append(updaters[i])
                            amp.append(1)
                    elif update[0:3] == 'Hat':
                        temp = str(js.get_button(int(update[4])))
                        if temp == update[6:]:
                            ID.append(updaters[i])
                            amp.append(1)
            axis = [abs(js.get_axis(i)) for i in xrange(js.get_numaxes())]
            hat = [js.get_hat(i) for i in xrange(js.get_numhats())]
            for event in pygame.event.get(): # Someone pressed a button!
                for js in window.joystick: # Who did that!
                    # Check each fundamental input type (button, axis, hat) for value
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            done = self.PyMOL_Command(['Escape'],[1])
                    if event.type == pygame.JOYBUTTONDOWN:
                        temp = js.get_button(event.button)
                        if temp > 0.1 and ('Button '+str(event.button)) in controls2_map:
                            ID.append(controls2[controls2_map.index('Button '+str(event.button))])
                            amp.append(1)
                    if event.type == pygame.JOYAXISMOTION:
                        if max(axis) > 0.8 and ('Axis '+str(axis.index(max(axis)))) in controls2_map: # Gradients can be buttons, if tilted beyond 80% max value
                            ID.append(controls2[controls2_map.index('Axis '+str(axis.index(max(axis))))])
                            amp.append(1)
                    if event.type == pygame.JOYHATMOTION: # Hat values are handled very weird, but they act funny with Pygame
                        if hat.count((0,0)) < len(hat):
                            temp = max([[i for i,v in enumerate(hat) if v != (0,0)][-1],-1])
                            if ('Hat '+str(temp)+' '+str(hat[temp])) in controls2_map:
                                ID.append(controls2[controls2_map.index('Hat '+str(temp)+' '+str(hat[temp]))])
                                amp.append(1)
            if ID: # If a command has been added
                done = self.PyMOL_Command(ID,amp)  # Let it ride into PyMOL
            cmd.refresh() # Refresh the display

    def PyMOL_Update(self): # This adds some basic information to the HUD in PyMOL
        lines = []
        lines.append('Structure: '+self.active[self.active_state%len(self.active)])
        lines.append('Residue Selection: '+self.seqs[self.active_state][self.index[self.active_state]][0])
        lines.append('Residue: '+self.seqs[self.active_state][self.index[self.active_state]][1])
        lines.append('Current Color: '+self.color[self.color_state%len(self.color)])
        lines.append('Current Show: '+self.show[self.show_state%len(self.show)])
        lines.append('')
        '''
        for i,j in zip(self.updaters,self.updaters_map):
            lines.append(i+': '+j)
        for i,j in zip(self.controls2,self.controls2_map):
            lines.append(i+': '+j)
        '''
        # Feel free to add more information if you want!
        self.window.Menu_Draw(lines)


'''
SECTION: TextPrint Class
PURPOSE: This is how text is formatted prior to getting printed to the screen
NOTE:
'''
class TextPrint:
    def __init__(self):
        self.f_size = 20
        self.reset()
        self.font = pygame.font.Font(None, self.f_size)   
    def print1(self, screen, textString):
        textBitmap = self.font.render(textString, True, BLACK)
        screen.blit(textBitmap, [self.x, self.y])
        self.y += self.line_height   
    def reset(self):
        self.x = self.f_size
        self.y = self.f_size
        self.line_height = self.f_size   
    def indent(self):
        self.x += self.f_size
    def unindent(self):
        self.x -= self.f_size

# This is how you can type without waiting for enter like raw_input (cleaner interface this way)
def TextInput(name,event):
    if event == pygame.K_BACKSPACE:
        return name[:-1],False
    elif event == pygame.K_LSHIFT or event == pygame.K_RSHIFT or event == pygame.K_TAB or event == pygame.K_MENU:
        return name,False
    elif event == pygame.K_ESCAPE:
        return name,True
    elif event == pygame.K_SPACE:
        return name+' ',False
    else:
        if pygame.key.get_mods() & pygame.KMOD_SHIFT:
            name += pygame.key.name(event).upper()
        else:
            name += pygame.key.name(event).lower()
        return name,False
    

'''
SECTION: Window Class
PURPOSE: Everything that goes into making the menu, and it is alot of technically junk
NOTE: Many snippets of this code comes directly from Pygame window examples
'''
class Window:
    def __init__(self,size = [400,600],cc=73,title='Settings Mode'): # We have a default window size and character count for centering strings
        # Set the width and height of the screen [width,height]
        self.cc = cc  #This is the spacing buffering for centering
        self.size = size #This is the size of the window (used later for centering text)
        self.screen = pygame.display.set_mode(size,0,0)
        pygame.display.set_caption(title)
            
        # Get ready to print
        self.textPrint = TextPrint()
        
        # Used to manage how fast the screen updates
        self.clock = pygame.time.Clock()
        
        # Get count of joysticks
        self.joystick_count = pygame.joystick.get_count()

        self.joystick = [pygame.joystick.Joystick(i) for i in xrange(self.joystick_count)]
        [a.init() for a in self.joystick]

    def Joy_ID(self,options=False,states=False):
        for js in window.joystick:
            button_count = js.get_numbuttons()
        if options:
            self.Menu_MAPPING_Layout(options,states,True,[' ','Press any key'])
            self.Menu_Draw(self.lines)
        ID = False
        while ID==False:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        ID = '    '
                else:
                    for js in window.joystick:
                        axis = [abs(js.get_axis(i)) for i in xrange(js.get_numaxes())]
                        hat = [js.get_hat(i) for i in xrange(js.get_numhats())]
                        if event.type == pygame.JOYBUTTONDOWN:
                            ID = 'Button '+str(event.button)
                        if event.type == pygame.JOYAXISMOTION:
                            if max(axis) > 0.8:
                                ID = 'Axis '+str(axis.index(max(axis)))
                        if event.type == pygame.JOYHATMOTION:
                            if hat.count((0,0)) < len(hat):
                                temp = [i for i,v in enumerate(hat) if v != (0,0)][-1]
                                ID = 'Hat '+str(temp)+' '+str(hat[temp])           
        return ID
        
    def Menu_Draw(self,lines,title='Menu',notes=[]):
        window.screen.fill(WHITE)
        window.textPrint.reset()
        for i in xrange((((self.size[1]/26)-2)-len(lines))/2):
            window.textPrint.print1(window.screen, ''.center(self.cc))
        window.textPrint.print1(window.screen, (' - '+title+' - ').center(self.cc))
        window.textPrint.print1(window.screen, ''.center(self.cc))
        for line in lines:
            window.textPrint.print1(window.screen, line.center(self.cc))
        for n in notes:
            window.textPrint.print1(window.screen, n.center(self.cc))
        pygame.display.flip()
        window.clock.tick(20)

    # Here, we develop 4 basic menu types: selection, toggle, mapping, manual
    # Depending what the user can modify, we create new ways to handle user input and layout the menu
    # Unfortunately, there wasn't a good way to compress this into a single function or atleast it was tricky
    def Menu_SELECTION(self,options):
        self.select = 0
        while True:
            # EVENT PROCESSING STEP
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return 'X'
                    if event.key == pygame.K_UP: self.select -= 1
                    if event.key == pygame.K_DOWN: self.select += 1
                    if event.key == pygame.K_RETURN: return self.select%len(options)
                if event.type == pygame.QUIT: return 'X'
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0: return self.select%len(options)
                    if event.button == 1: return 'X'
                if event.type == pygame.JOYHATMOTION:
                    self.select -= sum([window.joystick[i].get_hat(0)[1] for i in xrange(window.joystick_count)])
            self.Menu_SELECTION_Layout(options)
            self.Menu_Draw(self.lines)

    def Menu_SELECTION_Layout(self,options,notes=[]):
        self.lines = []
        for i in xrange(len(options)):
            if i == self.select%len(options):
                self.lines.append(('  >  '+options[i]+'  <  ').center(self.cc))
            else:
                self.lines.append(('     '+options[i]+'     ').center(self.cc))
        for line in notes:
            self.lines.append(line)

    def Menu_TOGGLE(self,options,states):
        self.select = 0
        while True:
            # EVENT PROCESSING STEP
            for event in pygame.event.get():
                select = self.select%(len(options)+1)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return 'X'
                    if event.key == pygame.K_UP: self.select -= 1
                    if event.key == pygame.K_DOWN: self.select += 1
                    if event.key == pygame.K_RETURN:
                        if select==len(options):
                            return 'X'
                        else:
                            states[select] = 1 - states[select]
                if event.type == pygame.QUIT: return 'X'
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:
                        if select==len(options):
                            return 'X'
                        else:
                            states[select] = 1 - states[select]
                    if event.button == 1: return 'X'
                if event.type == pygame.JOYHATMOTION:
                    self.select -= sum([self.joystick[i].get_hat(0)[1] for i in xrange(self.joystick_count)])
            self.Menu_TOGGLE_Layout(options,states)
            self.Menu_Draw(self.lines)

                
    def Menu_TOGGLE_Layout(self,options,states,notes=[]):
        self.lines = []
        select = self.select%(len(options)+1)
        self.lines.append(('  ON  |  OFF  ').center(self.cc))
        for index in xrange(len(options)):
            if select == index:
                if states[index] == 1:
                    self.lines.append((' > '+options[index]+' < :  X  |    ').center(self.cc))
                else:
                    self.lines.append((' > '+options[index]+' < :      |  X ').center(self.cc))
            else:
                if states[index] == 1:
                    self.lines.append(('    '+options[index]+'    :  X  |    ').center(self.cc))
                else:
                    self.lines.append(('    '+options[index]+'    :      |  X ').center(self.cc))
        if select == len(options):
            self.lines.append(' >  BACK  < ')
        else:
            self.lines.append('    BACK    ')
        for line in notes:
            self.lines.append(line)

    def Menu_STRINGS(self,options,states,exclusive=False,special=False,variables=False,pdb_test=False):
        self.select,self.special,self.variables,self.pdb_test = 0,special,variables,pdb_test
        while True:
            # EVENT PROCESSING STEP
            for event in pygame.event.get():
                select = self.select%(len(options)+3)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return self.variables
                    if event.key == pygame.K_UP: self.select -= 1
                    if event.key == pygame.K_DOWN: self.select += 1
                    if event.key == pygame.K_RETURN:
                        if select==len(options):
                            print 'Preparing to append'
                            options,states = self.Menu_STRINGS_Modify(options,states,select,'append')
                        elif select==len(options)+1:
                            print 'Preparing to delete'
                            options,states = self.Menu_STRINGS_Modify(options,states,select,'delete')
                        elif select==len(options)+2:
                            return self.variables
                        else:
                            if exclusive==True:
                                for i in xrange(len(options)):
                                    if i == select: states[i] = 1
                                    else: states[i] = 0
                            else:
                                states[select] = 1 - states[select]
                            if special:
                                self.variables = profiles.Load(options[select],self.variables)
                                print 'Self variables load'
                if event.type == pygame.QUIT: return self.variables
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:
                        if select==len(options):
                            print 'Preparing to append'
                            options,states = self.Menu_STRINGS_Modify(options,states,select,'append')
                        elif select==len(options)+1:
                            print 'Preparing to delete'
                            options,states = self.Menu_STRINGS_Modify(options,states,select,'delete')
                        elif select==len(options)+2:
                            return self.variables
                        else:
                            if exclusive==True:
                                for i in xrange(len(options)):
                                    if i == select: states[i] = 1
                                    else: states[i] = 0
                            else:
                                states[select] = 1 - states[select]
                            if special:
                                self.variables = profiles.Load(options[select],self.variables)
                    if event.button == 1: return self.variables
                if event.type == pygame.JOYHATMOTION:
                    self.select -= sum([self.joystick[i].get_hat(0)[1] for i in xrange(self.joystick_count)])
            self.Menu_STRINGS_Layout(options,states)
            self.Menu_Draw(self.lines)

    def Menu_STRINGS_Modify(self,options,states,index,change):
        name,done = '',False
        self.Menu_STRINGS_Layout(options,states,['Please enter name of entry to '+change+':',name])
        self.Menu_Draw(self.lines)
        while done == False:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if change == 'append':
                            if len(name) == 0:
                                self.Menu_STRINGS_Layout(options,states,['Please enter name of entry to '+change+':',name,'No name given. Please try again.'])
                                return options,states
                            else:
                                if self.special: profiles.Save(name,self.variables)
                                if self.pdb_test == True:
                                    if name.find('.pdb') == -1:
                                        name = name + '.pdb'
                                    if os.path.isfile(name):
                                        print 'File already exists!'
                                    else:                        
                                        print 'Searching protein databank for structure...'
                                        Fetch_PDB(name[:name.find('.pdb')])
                                        if os.path.isfile(name):
                                            print 'Structure located! Entry appended.'
                                        else:
                                            print 'Structure not found. Please try again.'
                                            return options,states
                                options.append(name)
                                states.append(0)
                                return options,states
                        elif change == 'delete':
                            if len(name) == 0:
                                self.Menu_STRINGS_Layout(options,states,['Please enter name of entry to '+change+':',name,'No name given. Please finish entry.'])
                                self.Menu_Draw(self.lines)
                            else:
                                try:
                                    if self.special: profiles.Delete(name)
                                    states.pop(options.index(name))
                                    options.pop(options.index(name))
                                    return options,states
                                except:
                                    self.Menu_STRINGS_Layout(options,states,['Unable to find entry. Be sure the name is correct.'])
                                    self.Menu_Draw(self.lines)
                                return options,states
                    else:
                        name,done = TextInput(name,event.key)
                        self.Menu_STRINGS_Layout(options,states,['Please enter name of entry to '+change+':',name])
                        self.Menu_Draw(self.lines)
        return options,states
        
    def Menu_STRINGS_Layout(self,options,states,notes=[]):
        self.lines = []
        
        select = self.select%(len(options)+3)
        self.lines.append(('  ON  |  OFF  ').center(self.cc))
        for index in xrange(len(options)):
            if select == index:
                if states[index] == 1:
                    self.lines.append((' > '+options[index]+' < :  X  |    ').center(self.cc))
                else:
                    self.lines.append((' > '+options[index]+' < :      |  X ').center(self.cc))
            else:
                if states[index] == 1:
                    self.lines.append(('    '+options[index]+'    :  X  |    ').center(self.cc))
                else:
                    self.lines.append(('    '+options[index]+'    :      |  X ').center(self.cc))
        if select == len(options):
            self.lines.append(' >  Append Entry  < ')
        else:
            self.lines.append('    Append Entry    ')
        if select == len(options)+1:
            self.lines.append(' >  Delete Entry  < ')
        else:
            self.lines.append('    Delete Entry    ')
        if select == len(options)+2:
            self.lines.append(' >  BACK  < ')
        else:
            self.lines.append('    BACK    ')
        for line in notes:
            self.lines.append(line)

    def Menu_MAPPING(self,options,states):
        self.select = 0
        while True:
            # EVENT PROCESSING STEP
            for event in pygame.event.get():
                select = self.select%(len(options)+1)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return 'X'
                    if event.key == pygame.K_UP: self.select -= 1
                    if event.key == pygame.K_DOWN: self.select += 1
                    if event.key == pygame.K_RETURN:
                        if select==len(options):
                            return 'X'
                        else:
                            states[select] = self.Joy_ID(options,states)
                if event.type == pygame.QUIT: return 'X'
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:
                        if select==len(options):
                            return 'X'
                        else:
                            states[select] = self.Joy_ID(options,states)
                    if event.button == 1: return 'X'
                if event.type == pygame.JOYHATMOTION:
                    self.select -= sum([self.joystick[i].get_hat(0)[1] for i in xrange(self.joystick_count)])
            self.Menu_MAPPING_Layout(options,states)
            self.Menu_Draw(self.lines)

                
    def Menu_MAPPING_Layout(self,options,states,focus=False,notes=[]):
        self.lines = []
        select = self.select%(len(options)+1)
        for index in xrange(len(options)):
            if select == index:
                if focus:
                    self.lines.append(('   '+options[index]+'     :   > '+states[index]+'  <').center(self.cc))
                else:
                    self.lines.append(('>  '+options[index]+'  <  :     '+states[index]+'   ').center(self.cc))
            else:
                self.lines.append(('     '+options[index]+'     :     '+states[index]+'   ').center(self.cc))
        if select == len(options):
            self.lines.append(' >  BACK  < ')
        else:
            self.lines.append('    BACK    ')
        for line in notes:
            self.lines.append(line)

'''
SECTION: Controls Class
PURPOSE: List out all the controls that map to a function in PyMOL
NOTE: You can make your own controls! See top for description.
'''
class Controls:
    def __init__(self,reset = False):
        if reset == True:
            self.options = ['Rotate (X)',
                            'Rotate (Y)',
                            'Rotate (Z)',
                            'Cycle colors (forward)',
                            'Cycle colors (backward)',
                            'Zoom (forward)',
                            'Zoom (backward)',
                            'Cycle Structures (forward)',
                            'Cycle Structures (backward)',
                            'Cycle display (forward)',
                            'Cycle display (backward)',
                            'Escape',
                            'Screen Lock',
                            'Reset View',
                            'Reset Molecule',
                            'Orient',
                            'Iterate Residue (forward)',
                            'Iterate Residue (backward)']
            self.states = ['Axis 3','Axis 4','Axis 0','Button 2','','Axis 2','','Button 4','Button 5','Button 3','','Button 6','Button 0','Button 1','Hat 0 (0, -1)','Hat 0 (0, 1)','Hat 0 (1, 0)','Hat 0 (-1, 0)']
            self.states += ['' for i in xrange(len(self.options)-len(self.states))]
            self.select = 0

    def Menu(self,window):
        done = False
        while not done=='X':
            # EVENT PROCESSING STEP
            done = window.Menu_MAPPING(self.options,self.states)
'''
SECTION: Settings Class
PURPOSE: Welcomes you to the menu, directs you to appropriate places for modifications
NOTE:
'''
class Settings:
    def __init__(self):
        self.options = ['Back to PyMOL','Controls','Structures','Profiles','Advanced Settings','Exit Session']

    def Menu(self,window,profiles,controls,structures,advanced):
        #Loop until the user clicks the close button.
        done = False
        while not done=='X':
            # EVENT PROCESSING STEP
            done = window.Menu_SELECTION(self.options)
            if done == 0: return False,controls,structures,advanced
            if done == 1: controls.Menu(window)
            if done == 2: structures.Menu(window)
            if done == 3: controls,structures,advanced = profiles.Menu(window,controls,structures,advanced)
            if done == 4: advanced.Menu(window)
            if done == 5: return True,controls,structures,advanced
        return False,controls,structures,advanced

    def Silent(self,filename,window,profiles,controls,structures,advanced):
        controls,structures,advanced = profiles.Quick_Load(window,filename,controls,structures,advanced)
        return False,controls,structures,advanced
'''
SECTION: Structures Class
PURPOSE: Can turn on and off structures
NOTE:
'''
class Structures:
    def __init__(self,reset = True):
        if reset == True:
            # Check if there are any files in directory
            self.pdbs = glob.glob('*.pdb')
            if len(self.pdbs) == 0:
                Fetch_PDB('1IGT')
                Fetch_PDB('2WNM')
                Fetch_PDB('1FNA')

            # Check if there are loaded structures to move to directory
            names = Preloaded_Structures()
            self.pdbs = glob.glob('*.pdb')

            if len(names) > 0:
                self.states = [0 for i in xrange(len(self.pdbs))]
                for name in names:
                    if name + '.pdb' in self.pdbs:
                        self.states[self.pdbs.index(name+'.pdb')] = 1
                    else:
                        print 'Could not activate structure: ' + name + '.pdb'
            else:
                self.states = [1 for i in xrange(len(self.pdbs))]
        
    def Menu(self,window):
        window.Menu_STRINGS(self.pdbs,self.states,pdb_test = True)

'''
SECTION: Profiles Class
PURPOSE: Saves both controls/settings AND current PyMOL session to .p/.pse files
NOTE: This allows you to recall all the visuals/controls you want at a future time
'''
class Profiles:
    def __init__(self):
        suffix = '_save.p'
        self.profiles = []
        for file in glob.glob('*'+suffix):
            self.profiles.append(file[:file.index(suffix)])
        if len(self.profiles) == 0:
            print 'No saved profiles... generating default.'
            controls,structures,advanced = self.Default()
        else:
            print 'Detected saves...'
            controls = Controls(True)
            structures = Structures(True)
            advanced = Advanced(True)
            self.states = [1 if i == 0 else 0 for i in xrange(len(self.profiles))]
        variables = [controls.options,controls.states,structures.pdbs,structures.states,advanced.colors,advanced.show]
        [controls.options,controls.states,structures.pdbs,structures.states,advanced.colors,advanced.show] = self.Load(self.profiles[0],variables)
        structures = Structures(True)  # On default, allow any structure in directory to be detected

        self.c,self.s,self.a = controls,structures,advanced
        self.kickstarter = False

    def Default(self):
        controls = Controls(True)
        structures = Structures(True)
        advanced = Advanced(True)
        self.Save('Default',[controls.options,controls.states,
                  structures.pdbs,structures.states,
                  advanced.colors,advanced.show])
        self.profiles = ['Default']
        cmd.save('Default.pse')
        self.states = [1]
        return controls,structures,advanced
        
    def Menu(self,window,controls,structures,advanced):
        variables = [controls.options,controls.states,structures.pdbs,structures.states,advanced.colors,advanced.show]
        variables = window.Menu_STRINGS(self.profiles,self.states,True,True,variables)
        [controls.options,controls.states,structures.pdbs,structures.states,advanced.colors,advanced.show] = variables
        return controls,structures,advanced

    def Quick_Load(self,filename,window,controls,structures,advanced):
        variables = [controls.options,controls.states,structures.pdbs,structures.states,advanced.colors,advanced.show]
        [controls.options,controls.states,structures.pdbs,structures.states,advanced.colors,advanced.show] = self.Load(filename,variables)
        return controls,structures,advanced

    def Save(self,filename,variables):
        # If all structures are not loaded, quick! Load them now
        structures = cmd.get_object_list('all') # Figure out what's already loaded so we dont cover up existing structures
        self.seqs = []
        # Pulls up the active structures lists and quickloads them before saving
        # actives = [i[:-4] for i,j in zip(self.s.pdbs,self.s.states) if j == 1]
        actives = [i[:-4] for i,j in zip(variables[2],variables[3]) if j == 1]
        for active in actives:  # Iterate through all active PDBs (dictated by menu)
            if not active in structures: # If its not already loaded...
                print 'Loading %s ...' % active
                time.sleep(.25)
        cmd.refresh()
        time.sleep(.25)
        # Resume with committing all the scene and settings files to saved file equivalents
        pickle.dump(variables,open(filename+'_save.p','wb'))
        cmd.save(filename+'.pse')
        print 'All variables saved under %s _save.p.' % filename 
        
    def Load(self,filename,variables = None):
        suffix = '_save.p'
        self.kickstarter = True
        try:
            variables = pickle.load(open(filename+suffix,'rb'))
        except:
            print 'Files not located. Returning unmodified files...'
            if not(variables):
                raise Exception('Variables file not properly referenced in function')
            #variables = pickle.load(open(filename,'rb'))
        #[controls.options,controls.states,structures.pdbs,structures.states,advanced.colors,advanced.show] = variables
        #return controls,structures,advanced
        return variables
        
    def Delete(self,filename):
        suffix = '_save.p'
        save = os.remove(filename+suffix)

'''
SECTION: Advanced Class
PURPOSE: Takes care of the stuff that doesn't quite fit into other menus
NOTE: Currently, this only handles which colors you can activate, and which structure features can be shown
'''
class Advanced:
    def __init__(self,reset = False):
        if reset == True:
            self.colors = [['red','blue','green','teal','yellow','white'],[1,1,1,1,1,1]]
            self.show = [['lines','sticks','cartoon','mesh','ribbon','dots','surface','slice','cell'],[1,1,1,1,0,1,0,0,0,0]]
        self.options2 = ['Colors','Structure','BACK']

    def Menu(self,window):
        #Loop until the user clicks the close button.
        done = False
        while not done=='X':
            # EVENT PROCESSING STEP
            done = window.Menu_SELECTION(self.options2)
            if done == 0: self.Color_Menu(window)
            if done == 1: self.Structure_Menu(window)
            if done == 2: done = 'X'
        print 'Exiting...'

    def Color_Menu(self,window):
        window.Menu_STRINGS(self.colors[0],self.colors[1])

    def Structure_Menu(self,window):
        window.Menu_STRINGS(self.show[0],self.show[1])


def PyMOL360(filename=None):
    
    ### Here are some global variables that you can change if you prefer
    global sensitivity, window, profiles, settings
    # Sensitivity of rotation
    sensitivity = 5.

    # For now, this is where we move to a new directory holding structures and saved files
    directory = './PyMOL360/'
    if not os.path.exists(directory):
        os.makedirs(directory)
    os.chdir(directory)
    
    run = True

    try:
        import pygame
    except:
        print 'Pygame module not found in PyMOL Python instance. Please see README.txt for instructions on installation.'
        run = False

    # Initialize pygame module
    try:
        pygame.init()
        pygame.display.init()
        pygame.font.init()
        pygame.joystick.init()
        print 'Pygame modules initialized.'
    except:
        print 'Pygame not initializing properly, restart may be required.'

    # General error handling (needs to have module shutdown even if errors are encountered)
    try:
        if run == False:
            print 'Exiting...'
        elif pygame.joystick.get_count() == 0:
            print 'No joysticks detected, check connectivity.'
        else:
            print 'Input arguments:',filename
            if filename:
                print 'Entering silent mode...'
                print 'Selected filename:',filename
                # Continue with (mostly) normal startup
                pymol = PyMOL()
                settings = Settings()
                profiles = Profiles()
                window = Window()
                done,profiles.c,profiles.s,profiles.a = settings.Silent(window,filename,profiles,profiles.c,profiles.s,profiles.a)
                active = [i[:-4] for i,j in zip(profiles.s.pdbs,profiles.s.states) if j == 1]
                pymol.Menu(profiles.c.options,profiles.c.states,profiles.a,active,filename)
                
            else:
                # Initialize all the major classes
                pymol = PyMOL()
                settings = Settings()
                profiles = Profiles()

                done = False

                # Main operating loop, enables you to go back and forth between menu and PyMOL indefinitely
                while done == False: # If done value is switched, it'll kick you out of the script real quick
                    window = Window()
                    done,profiles.c,profiles.s,profiles.a = settings.Menu(window,profiles,profiles.c,profiles.s,profiles.a)
                    active = [i[:-4] for i,j in zip(profiles.s.pdbs,profiles.s.states) if j == 1]
                    if done == False: pymol.Menu(profiles.c.options,profiles.c.states,profiles.a,active)

            print 'Exiting...'
            # Close the window and quit.
            # If you forget this line, the program will 'hang'
            # on exit if running from IDLE.
            
    # Error catching without full script shutdown, ensuring modules get exitting appropriately
    except Exception,e:
        print 'PyMOL360 error...'
        print "<p>Error: %s</p>" % e
        
    # This closes the window between operations
    os.chdir('..')
    pygame.display.quit()
    pygame.joystick.quit()
    # Note: due to some issues with pygame 1.9.2, the system CANNOT shut down the font/joystick modules
    # This will cause the system to crash with "Text has zero width" error
    # This has to deal with the fact we are running out of a shell in PyMOL rather than a personal instance of Python

    time.sleep(0.5)

    print 'Exited.'

# Three common ways to call PyMOL360
cmd.extend('PYMOL360',PyMOL360)
cmd.extend('PyMOL360',PyMOL360)
cmd.extend('PyMol360',PyMOL360)
cmd.extend('pymol360',PyMOL360)
            

