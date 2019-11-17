import pygame
# not positive whats in this library: for event handling 
from pygame.locals import *
import threading
import sys
import os

# to change later
FONT = 'typewriter_condensed/typewcond_regular.otf'

# screen dimentions
SCREEN_SIZE = (800,600)
STARTING_SCREEN = "Welcome"
white = (255, 255, 255)
black = (0, 0, 0)

def print_message(screen, message, x, y):
    font = pygame.font.Font(FONT, 32)
    text = font.render(message, True, black)
    textRect = text.get_rect()
    textRect.center = (x, y)
    screen.blit(text, textRect)

def button(screen,msg,x,y,w,h,ic,ac,action=None):
    if x+w > pygame.mouse.get_pos()[0] > x and y+h > pygame.mouse.get_pos()[1] > y:
        pygame.draw.rect(screen, ac,(x,y,w,h))

        if pygame.mouse.get_pressed()[0] == 1 and action != None:
            action()
    else:
        pygame.draw.rect(screen, ic,(x,y,w,h))

    smallText = pygame.font.Font(FONT,20)
    textSurf  = smallText.render(msg, True, black)
    textRect  = textSurf.get_rect()
    textRect.center = ( (x+(w/2)), (y+(h/2)) )
    screen.blit(textSurf, textRect)

# def selection(screen,msg,x,y,w,h,ic,ac,action=None):
#     if x+w > pygame.mouse.get_pos()[0] > x and y+h > pygame.mouse.get_pos()[1] > y:
#         pygame.draw.rect(screen, ac,(x,y,w,h))

#         if pygame.mouse.get_pressed()[0] == 1 and action != None:
#             action()
#     else:
#         pygame.draw.rect(screen, ic,(x,y,w,h))

#     smallText = pygame.font.Font(FONT,20)
#     textSurf  = smallText.render(msg, True, black)
#     textRect  = textSurf.get_rect()
#     textRect.center = ( (x+(w/2)), (y+(h/2)) )
#     screen.blit(textSurf, textRect)

# def text_box:
#     for event in pygame.event.get():
#         # if event is quit then set doen to true
#         if event.type == pygame.QUIT:
#             done = True

#         if event.type == pygame.MOUSEBUTTONDOWN:
#             # If the user clicked on the input_box rect.
#             if input_box.collidepoint(event.pos):
#                 # Toggle the active variable.
#                 active = not active
#             else:
#                 active = False

#         color = color_active if active else color_inactive

#         if event.type == pygame.KEYDOWN:
#             if active:
#                 if event.key == pygame.K_RETURN:
#                     print(text)
#                     text = ''
#                 elif event.key == pygame.K_BACKSPACE:
#                     text = text[:-1]
#                 else:
#                     text += event.unicode

#         # Render the current text.
#         txt = font_small.render(text, True, color)

#         # Resize the box if the text is too long.
#         width = max(200, txt.get_width()+10)
#         input_box.w = width

#         # centers text in box 
#         screen.blit(txt, (input_box.x+5, input_box.y+5))
#         # Blit the input_box rect.
#         pygame.draw.rect(screen, color, input_box, 2)



class gameScreen:

    def __init__(self, Story):
        self.done = False
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        self.screen.fill(white)
        self.game_state = [STARTING_SCREEN]
        self.entry = ""
        self.submissions = []
        self.vote = 0
        self.scenes = Story
        self.clock = pygame.time.Clock()
        # change to game name later
        pygame.display.set_caption("concurrent ass kicking")


    def run(self):
        while True:
            # if no states left then quit
            if not self.game_state:
                break

            # get next state
            next_state = self.game_state.pop()
            function_name = next_state.replace(" ","")

            # if next state is a valid function then call it, otherwise quit
            if hasattr(self,function_name):
                function = getattr(self,function_name)
                function()
            else:
                break

    def add_submission(self, submission):
        self.submissions.append(submission)

    def get_vote(self):
        return self.vote

    def get_submission(self):
        return self.entry


    def Welcome(self):
        blue = pygame.Color('lightskyblue3')
        darker_blue = pygame.Color('dodgerblue2')

        self.done = False

        while not self.done:
            ## Handle messages from elsewhere, such as the interface.
            # for message in self.messages:
            #     headline = message.get("headline","")
            #     print "Got a message: "+headline

            # self.messages = []

            ## Handle events.
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.done = True
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.done = True

            print_message(self.screen, "Welcome!", 400, 200)
            #add last argument of function to run
            def next_submit():
                self.game_state.append("Game Screen")
                self.done = True

            button(self.screen,"Start!",350,450,100,50,blue,darker_blue,next_submit)

            pygame.display.update()
            self.clock.tick(50)

    def GameScreen(self):
        blue = pygame.Color('lightskyblue3')
        darker_blue = pygame.Color('dodgerblue2')

        self.done = False

        if len(self.scenes) > 0:
            scene = self.scenes.pop(0)
        else:
            self.game_state.append("Game End")
            self.done = True;

        while not self.done:
            ## Handle messages from elsewhere, such as the interface.
            # for message in self.messages:
            #     headline = message.get("headline","")
            #     print "Got a message: "+headline

            # self.messages = []

            ## Handle events.
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.done = True
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.done = True

            self.screen.fill(white)
            print_message(self.screen, scene, 400, 200)
            
            #add last argument of function to run

            def next_vote():
                self.game_state.append("Vote")
                self.done = True

            button(self.screen,"submit",400,450,100,50,blue,darker_blue,next_vote)

            pygame.display.update()
            self.clock.tick(50)

    def Vote(self):
        blue = pygame.Color('lightskyblue3')
        darker_blue = pygame.Color('dodgerblue2')

        self.done = False

        entries = []

        while not self.done:

            ## Handle events.
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.done = True
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.done = True

            self.screen.fill(white)
            print_message(self.screen, "submissions:", 400, 100)

            #add last argument of function to run
            while len(self.submissions) != 0:
                entries.append(self.submissions.pop(0))

            for entry in entries:
                num, text = entry
                #print_message(self.screen, text, 400, 100 + 50 * num)
                button(self.screen,text,400,100 + 50 * num,100,50,blue,darker_blue)

            def next_vote():
                self.game_state.append("Game Screen")
                self.done = True

            button(self.screen,"vote",650,450,100,50,blue,darker_blue,next_vote)

            pygame.display.update()
            self.clock.tick(50)

        self.submissions = []

    def GameEnd(self):
        blue = pygame.Color('lightskyblue3')
        darker_blue = pygame.Color('dodgerblue2')

        self.done = False

        while not self.done:

            for event in pygame.event.get():
                if event.type == QUIT:
                    self.done = True
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.done = True

            self.screen.fill(white)
            print_message(self.screen, "Thanks for playing!", 400, 200)

            pygame.display.update()
            self.clock.tick(50)




    # def display_screen():

    #     welcome = welcome()
    #     screen = initialize()

    #     clock = pygame.time.Clock()

    #     # start done as false to enter infinite loop
    #     done = False

    #     print_message(screen, 'scene: ', 400, 150)
    #     print_message(screen, 'response: ', 400, 300)

    #     # makes text box
    #     font_small = pygame.font.Font('typewriter_condensed/typewcond_regular.otf', 16)
    #     input_box = pygame.Rect(100, 100, 140, 32)
    #     text = ''
    #     input_box.center = (X / 2 - 30, (Y * 2 / 3)) 
    #     color_inactive = pygame.Color('lightskyblue3')
    #     color_active = pygame.Color('dodgerblue2')
    #     color = color_inactive
    #     active = False

    #     while not done:

    #         # get events from queue and excecute
    #         for event in pygame.event.get():
    #             # if event is quit then set doen to true
    #             if event.type == pygame.QUIT:
    #                 done = True

    #             if event.type == pygame.MOUSEBUTTONDOWN:
    #                 # If the user clicked on the input_box rect.
    #                 if input_box.collidepoint(event.pos):
    #                     # Toggle the active variable.
    #                     active = not active
    #                 else:
    #                     active = False

    #             color = color_active if active else color_inactive

    #             if event.type == pygame.KEYDOWN:
    #                 if active:
    #                     if event.key == pygame.K_RETURN:
    #                         print(text)
    #                         text = ''
    #                     elif event.key == pygame.K_BACKSPACE:
    #                         text = text[:-1]
    #                     else:
    #                         text += event.unicode

    #             # Render the current text.
    #             txt = font_small.render(text, True, color)

    #             # Resize the box if the text is too long.
    #             width = max(200, txt.get_width()+10)
    #             input_box.w = width

    #             # centers text in box 
    #             screen.blit(txt, (input_box.x+5, input_box.y+5))
    #             # Blit the input_box rect.
    #             pygame.draw.rect(screen, color, input_box, 2)


    #         # make updates visible to user
    #         pygame.display.flip()
    #         clock.tick(60)

#for texting purposes:
def monitor_game(game):
    text = input("submission: ")
    num = 0;
    while num < 4:
        num += 1
        game.add_submission((num, text))
        print(num)
        text = input("submission:")


pygame.init()
game = gameScreen(["scene 1", "scene 2", "scene 3"])
monitor = threading.Thread(target=monitor_game, args=(game, ))
monitor.start()
game.run()
monitor.join()
pygame.quit()