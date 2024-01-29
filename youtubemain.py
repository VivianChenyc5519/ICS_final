import pygame
import sys
import random
from words import *


class Letter:
    def __init__(self, text, bg_position, LETTER_SIZE, GUESSED_LETTER_FONT, SCREEN, FILLED_OUTLINE, OUTLINE):
        # Initializes all the variables, including text, color, position, size, etc.
        self.GUESSED_LETTER_FONT = GUESSED_LETTER_FONT
        self.SCREEN = SCREEN
        self.FILLED_OUTLINE = FILLED_OUTLINE
        self.OUTLINE = OUTLINE
        self.bg_color = "white"
        self.text_color = "black"
        self.bg_position = bg_position
        self.bg_x = bg_position[0]
        self.bg_y = bg_position[1]
        self.bg_rect = (bg_position[0], self.bg_y, LETTER_SIZE, LETTER_SIZE)
        self.text = text
        self.text_position = (self.bg_x + 36, self.bg_position[1] + 34)
        self.text_surface = self.GUESSED_LETTER_FONT.render(
            self.text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect(center=self.text_position)

    def draw(self):
        # Puts the letter and text on the screen at the desired positions.
        pygame.draw.rect(self.SCREEN, self.bg_color, self.bg_rect)
        if self.bg_color == "white":
            pygame.draw.rect(self.SCREEN, self.FILLED_OUTLINE, self.bg_rect, 3)
        self.text_surface = self.GUESSED_LETTER_FONT.render(
            self.text, True, self.text_color)
        self.SCREEN.blit(self.text_surface, self.text_rect)
        pygame.display.update()

    def delete(self):
        # Fills the letter's spot with the default square, emptying it.
        pygame.draw.rect(self.SCREEN, "white", self.bg_rect)
        pygame.draw.rect(self.SCREEN, self.OUTLINE, self.bg_rect, 3)
        pygame.display.update()


# =============================================================================
# class Indicator:
#     def __init__(self, x, y, letter, SCREEN, OUTLINE, AVAILABLE_LETTER_FONT):
#         # Initializes variables such as color, size, position, and letter.
#         self.x = x
#         self.y = y
#         self.text = letter
#         self.rect = (self.x, self.y, 57, 75)
#         self.bg_color = OUTLINE
#         self.SCREEN = SCREEN
#         self.AVAILABLE_LETTER_FONT = AVAILABLE_LETTER_FONT
#
#     def draw(self):
#         # Puts the indicator and its text on the screen at the desired position.
#         pygame.draw.rect(self.SCREEN, self.bg_color, self.rect)
#         self.text_surface = self.AVAILABLE_LETTER_FONT.render(self.text, True, "white")
#         self.text_rect = self.text_surface.get_rect(center=(self.x + 27, self.y + 30))
#         self.SCREEN.blit(self.text_surface, self.text_rect)
#         pygame.display.update()
# =============================================================================

class LetterGame:

    def __init__(self):
        pygame.init()

        # Constants

        self.WIDTH, self.HEIGHT = 633, 800

        self.SCREEN = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.BACKGROUND = pygame.image.load("assets/Starting Tiles.png")
        self.BACKGROUND_RECT = self.BACKGROUND.get_rect(center=(317, 300))

        pygame.display.set_caption("Wordle!")

        self.GREEN = "#6aaa64"
        self.YELLOW = "#c9b458"
        self.GREY = "#787c7e"
        self.OUTLINE = "#d3d6da"
        self.FILLED_OUTLINE = "#878a8c"

        self.CORRECT_WORD = "coder"

        self.ALPHABET = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]

        self.GUESSED_LETTER_FONT = pygame.font.Font(
            "assets/FreeSansBold.otf", 50)
        self.AVAILABLE_LETTER_FONT = pygame.font.Font(
            "assets/FreeSansBold.otf", 25)

        self.SCREEN.fill("white")
        self.SCREEN.blit(self.BACKGROUND, self.BACKGROUND_RECT)
        pygame.display.update()

        self.LETTER_X_SPACING = 85
        self.LETTER_Y_SPACING = 12
        self.LETTER_SIZE = 75

        # Global variables

        self.guesses_count = 0

        # guesses is a 2D list that will store guesses. A guess will be a list of letters.
        # The list will be iterated through and each letter in each guess will be drawn on the screen.
        self.guesses = [[]] * 6

        self.current_guess = []
        self.current_guess_string = ""
        self.current_letter_bg_x = 110

        # Indicators is a list storing all the Indicator object. An indicator is that button thing with all the letters you see.
        #self.indicators = []

        self.game_result = ""
        self.main()

    def check_guess(self, guess_to_check):
        # Goes through each letter and checks if it should be green, yellow, or grey.
        self.game_decided = False

        for i in range(5):
            lowercase_letter = guess_to_check[i].text.lower()
            if lowercase_letter in self.CORRECT_WORD:
                if lowercase_letter == self.CORRECT_WORD[i]:
                    guess_to_check[i].bg_color = self.GREEN
# =============================================================================
#                     for indicator in self.indicators:
#                         if indicator.text == lowercase_letter.upper():
#                             indicator.bg_color = self.GREEN
#                             indicator.draw()
# =============================================================================
                    guess_to_check[i].text_color = "white"
                    if not self.game_decided:
                        self.game_result = "W"
                else:
                    guess_to_check[i].bg_color = self.YELLOW
# =============================================================================
#                     for indicator in self.indicators:
#                         if indicator.text == lowercase_letter.upper():
#                             indicator.bg_color = self.YELLOW
#                             indicator.draw()
# =============================================================================
                    guess_to_check[i].text_color = "white"
                    self.game_result = ""
                    self.game_decided = True
            else:
                guess_to_check[i].bg_color = self.GREY
# =============================================================================
#                 for indicator in self.indicators:
#                     if indicator.text == lowercase_letter.upper():
#                         indicator.bg_color = self.GREY
#                         indicator.draw()
# =============================================================================
                guess_to_check[i].text_color = "white"
                self.game_result = ""
                self.game_decided = True
            guess_to_check[i].draw()
            pygame.display.update()

        self.guesses_count += 1
        self.current_guess = []
        self.current_guess_string = ""
        self.current_letter_bg_x = 110

        if self.guesses_count == 6 and self.game_result == "":
            self.game_result = "L"

    def play_again(self):
        # Puts the play again text on the screen.
        pygame.draw.rect(self.SCREEN, "white", (10, 600, 1000, 600))
        play_again_font = pygame.font.Font("assets/FreeSansBold.otf", 40)
        play_again_text = play_again_font.render(
            "Press ENTER to Play Again!", True, "black")
        play_again_rect = play_again_text.get_rect(center=(self.WIDTH/2, 700))
        word_was_text = play_again_font.render(
            f"The word was {self.CORRECT_WORD}!", True, "black")
        word_was_rect = word_was_text.get_rect(center=(self.WIDTH/2, 650))
        self.SCREEN.blit(word_was_text, word_was_rect)
        self.SCREEN.blit(play_again_text, play_again_rect)
        pygame.display.update()

    def instruction(self):
        pygame.draw.rect(self.SCREEN, "white", (10, 600, 1000, 600))
        ins_font = pygame.font.Font("assets/FreeSansBold.otf", 30)
        ins_text_green = ins_font.render(
            "Green: right alphabet, right position", True, self.GREEN)
        ins_rect_green = ins_text_green.get_rect(center=(self.WIDTH/2, 650))
        ins_text_yellow = ins_font.render(
            "Yellow: right alphabet, wrong position", True, self.YELLOW)
        ins_rect_yellow = ins_text_yellow.get_rect(center=(self.WIDTH/2, 700))
        ins_text_grey = ins_font.render(
            "Grey: wrong alphabet, wrong position", True, self.GREY)
        ins_rect_grey = ins_text_grey.get_rect(center=(self.WIDTH/2, 750))
        self.SCREEN.blit(ins_text_green, ins_rect_green)
        self.SCREEN.blit(ins_text_yellow, ins_rect_yellow)
        self.SCREEN.blit(ins_text_grey, ins_rect_grey)
        pygame.display.update()

    def reset(self):
        # Resets all global variables to their default states.
        self.SCREEN.fill("white")
        self.SCREEN.blit(self.BACKGROUND, self.BACKGROUND_RECT)
        self.guesses_count = 0
        self.CORRECT_WORD = random.choice(WORDS)
        self.guesses = [[]] * 6
        self.current_guess = []
        self.current_guess_string = ""
        self.game_result = ""
        pygame.display.update()
# =============================================================================
#         for indicator in self.indicators:
#             indicator.bg_color = self.OUTLINE
#             indicator.draw()
# =============================================================================

    def create_new_letter(self):
        # Creates a new letter and adds it to the guess.
        self.current_guess_string += self.key_pressed
        self.new_letter = Letter(self.key_pressed, (self.current_letter_bg_x, self.guesses_count*100+self.LETTER_Y_SPACING),
                                 self.LETTER_SIZE, self.GUESSED_LETTER_FONT, self.SCREEN, self.FILLED_OUTLINE, self.OUTLINE)
        self.current_letter_bg_x += self.LETTER_X_SPACING
        self.guesses[self.guesses_count].append(self.new_letter)
        self.current_guess.append(self.new_letter)
        for guess in self.guesses:
            for letter in guess:
                letter.draw()

    def delete_letter(self):
        # Deletes the last letter from the guess.
        self.guesses[self.guesses_count][-1].delete()
        self.guesses[self.guesses_count].pop()
        self.current_guess_string = self.current_guess_string[:-1]
        self.current_guess.pop()
        self.current_letter_bg_x -= self.LETTER_X_SPACING

    def main(self):
        flg = True
        while flg:
            if self.game_result != "":
                self.play_again()
            else:
                self.instruction()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    flg = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if self.game_result != "":
                            self.reset()
                        else:
                            if len(self.current_guess_string) == 5:
                                self.check_guess(self.current_guess)
                    elif event.key == pygame.K_BACKSPACE:
                        if len(self.current_guess_string) > 0:
                            self.delete_letter()
                    else:
                        self.key_pressed = event.unicode.upper()
                        if self.key_pressed in "QWERTYUIOPASDFGHJKLZXCVBNM" and self.key_pressed != "":
                            if len(self.current_guess_string) < 5:
                                self.create_new_letter()


if __name__ == "__main__":
    game = LetterGame()
