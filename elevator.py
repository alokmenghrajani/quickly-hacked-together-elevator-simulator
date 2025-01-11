import pygame
import time
from enum import Enum

# A quickly hacked-together elevator simulator for the purpose of conducting
# technical interviews.
# (c) 2025 Alok Menghrajani. All rights reserved.

# The candidate's goal is to fill the implementation for ElevatorLogic, a class
# which controls the elevator's movements.

class ElevatorLogicResponse(Enum):
  STOP = "stop"
  UP = "up"
  DOWN = "down"

class ElevatorLogic:
  # Called once at initialization time. Floors is the total number of floors.
  def __init__(self, floors):
    pass

  # Called when a call button is pressed. Floors are numbered as 0 for the
  # lowest (ground) floor and counting upwards.
  def handle_call_button(self, floor_number):
    pass
  
  # Called when the elevator is arriving at a given floor. The function must
  # return one of ElevatorLogicResponse. If the elevator stops, the function
  # is called again with the same floor_number after the doors close.
  def handle_arriving_at(self, floor_number):
    pass

################################################################################

# The candidate can look at the code below but they shouldn't need to know about
# it or modify it.

def main():
  clock = pygame.time.Clock()

  world_view = WorldView()
  world_controller = WorldController(world_view)
  
  running = True
  while running:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        running = False
      
      if event.type == pygame.MOUSEMOTION:
        mouse_pos = pygame.mouse.get_pos()
        world_controller.handle_mouse_move(mouse_pos[0], mouse_pos[1])
      elif event.type == pygame.MOUSEBUTTONDOWN:
        mouse_pos = pygame.mouse.get_pos()
        world_controller.handle_click(mouse_pos[0], mouse_pos[1])
      
    world_controller.update()
    pygame.display.flip()
    clock.tick(60) # 60 FPS
  pygame.quit()

# Our world consists of:
# - five call buttons (one per floor)
# - one elevator
#
# The code has been structured to make it easier to extend in the future:
# - have people which appear randomly at a given floor and want to go to
#   another floor.
# - have additional buttons (e.g. up/down button on each floor).
# - have additional elevators.

class WorldModel:
  WIDTH = 1200
  HEIGHT = 800
  MARGIN = 20
  FLOORS = 5
  TITLE = "quickly-hacked-together-elevator-simulator"

class WorldView:
  BACKGROUND_COLOR = (255, 255, 255) # white
  FLOOR_COLOR = (0, 0, 0) # black
  TEXT_SIZE = 20
  TEXT_COLOR = (0x66, 0x9b, 0xbc)

  def __init__(self):
    pygame.init()
    pygame.font.init()
    self.font = pygame.font.Font(None, WorldView.TEXT_SIZE)
    self.screen = pygame.display.set_mode((WorldModel.WIDTH, WorldModel.HEIGHT))
    pygame.display.set_caption(WorldModel.TITLE)
    self.initialized = True
  
  def floor_height():
    return (WorldModel.HEIGHT - 2 * WorldModel.MARGIN) / WorldModel.FLOORS

  def floor_to_y(floor):
    return int(WorldModel.HEIGHT - floor * WorldView.floor_height() - WorldModel.MARGIN)

  def draw(self):
    self.screen.fill(WorldView.BACKGROUND_COLOR)

    # Draw lines for each floor
    for floor in range(WorldModel.FLOORS):
      y = WorldView.floor_to_y(floor)
      pygame.draw.line(self.screen, WorldView.FLOOR_COLOR, (WorldModel.MARGIN, y), (WorldModel.WIDTH - WorldModel.MARGIN, y))
      floor_text = self.font.render(f"Floor {floor}", True, WorldView.TEXT_COLOR)
      self.screen.blit(floor_text, (WorldModel.MARGIN, y - WorldView.TEXT_SIZE))

class WorldController:
  def __init__(self, view):
    self.view = view

    elevator_model = ElevatorModel()
    elevator_view = ElevatorView()
    self.elevator_controller = ElevatorController(elevator_model, elevator_view)
    self.call_button_controllers = []
    for floor in range(WorldModel.FLOORS):
      model = ButtonModel(x=WorldModel.WIDTH - WorldModel.MARGIN - 60, y=WorldView.floor_to_y(floor) - 62, width=60, height=60, label="call")
      self.call_button_controllers.append(ButtonController(model, ButtonView(self.view.font, WorldView.TEXT_SIZE)))
    
    self.elevator_logic = ElevatorLogic(WorldModel.FLOORS)

  def handle_mouse_move(self, x, y):
    for call_button_controller in self.call_button_controllers:
      call_button_controller.handle_mouse_move(x, y)

  def handle_click(self, x, y):
    for i in range(len(self.call_button_controllers)):
      call_button_controller = self.call_button_controllers[i]
      if call_button_controller.handle_click(x, y):
        self.elevator_logic.handle_call_button(i)

  def update(self):
    self.view.draw()
    self.elevator_controller.update(self.view.screen, self.elevator_logic, self.call_button_controllers)
    for call_button_controller in self.call_button_controllers:
      call_button_controller.update(self.view.screen)

################################################################################

# Elevator
class ElevatorState(Enum):
  IDLE = "idle"
  MOVING_UP = "moving_up"
  MOVING_DOWN = "moving_down"
  DOORS_OPENING = "doors_opening"
  DOORS_CLOSING = "doors_closing"
  DOORS_OPEN = "doors_open"

class ElevatorModel:
  def __init__(self):
    self.current_floor = 0
    self.state = ElevatorState.IDLE
    self.value = 0

class ElevatorView:
  COLOR = (0x00, 0x30, 0x49)
  WIDTH = 80
  HEIGHT = 100
  DOOR_COLOR = (255, 0, 0)
  DOOR_HEIGHT = 98
  DOOR_GAP = 2
  X = 100
  DOOR_SPEED = 1 # in 100*FPS

  def __init__(self):
    pass

  def draw(self, model, screen):
    # Compute elevator's y position
    y = WorldView.floor_to_y(model.current_floor)
    if model.state == ElevatorState.MOVING_UP:
      y -= WorldView.floor_height() * model.value / 100
    elif model.state == ElevatorState.MOVING_DOWN:
      y += WorldView.floor_height() * model.value / 100

    pygame.draw.rect(screen, ElevatorView.COLOR, (ElevatorView.X, y - ElevatorView.HEIGHT, ElevatorView.WIDTH, ElevatorView.HEIGHT))

    # Compute the position of the doors
    x = ElevatorView.X + ElevatorView.WIDTH / 2
    if model.state == ElevatorState.DOORS_OPENING:
      door_width = (100 - model.value) / 100 * (ElevatorView.WIDTH / 2 - 2 * ElevatorView.DOOR_GAP) + ElevatorView.DOOR_GAP
    elif model.state == ElevatorState.DOORS_CLOSING:
      door_width = model.value / 100 * (ElevatorView.WIDTH / 2 - 2 * ElevatorView.DOOR_GAP) + ElevatorView.DOOR_GAP
    elif model.state == ElevatorState.DOORS_OPEN:
      door_width = ElevatorView.DOOR_GAP
    else:
      door_width = (ElevatorView.WIDTH - ElevatorView.DOOR_GAP) / 2 

    pygame.draw.rect(screen, ElevatorView.DOOR_COLOR, (ElevatorView.X, y - ElevatorView.DOOR_HEIGHT, door_width, ElevatorView.DOOR_HEIGHT))
    pygame.draw.rect(screen, ElevatorView.DOOR_COLOR, (ElevatorView.X + ElevatorView.WIDTH - door_width, y - ElevatorView.DOOR_HEIGHT, door_width, ElevatorView.DOOR_HEIGHT))

class ElevatorController:
  def __init__(self, model, view):
    self.model = model
    self.view = view
  
  def update(self, screen, elevator_logic, call_button_controllers):
    self.model.value = self.model.value + 1
    if (self.model.state == ElevatorState.DOORS_OPENING or
      self.model.state == ElevatorState.DOORS_OPEN):
      call_button_controllers[self.model.current_floor].clear()

    if self.model.value == 100:
      self.model.value = 0
      callback = False
      match self.model.state:
        case ElevatorState.DOORS_OPENING:
          self.model.state = ElevatorState.DOORS_OPEN
        case ElevatorState.DOORS_OPEN:
          self.model.state = ElevatorState.DOORS_CLOSING
        case ElevatorState.DOORS_CLOSING:
          callback = True
        case ElevatorState.MOVING_UP:
          self.model.current_floor += 1
          callback = True
        case ElevatorState.MOVING_DOWN:
          self.model.current_floor -= 1
          callback = True
        case ElevatorState.IDLE:
          callback = True

      if callback:
        r = elevator_logic.handle_arriving_at(self.model.current_floor)
        match r:
          case ElevatorLogicResponse.STOP:
            self.model.state = ElevatorState.DOORS_OPENING
          case ElevatorLogicResponse.UP:
            self.model.state = ElevatorState.MOVING_UP
            if self.model.current_floor == (WorldModel.FLOORS - 1):
              self.model.state = ElevatorState.IDLE
          case ElevatorLogicResponse.DOWN:
            self.model.state = ElevatorState.MOVING_DOWN
            if self.model.current_floor == 0:
              self.model.state = ElevatorState.IDLE
          case None:
            self.model.state = ElevatorState.IDLE
          case _:
            raise Exception("invalid response: {}".format(r))

    self.view.draw(self.model, screen)

################################################################################

# Button
class ButtonModel:
  def __init__(self, x, y, width, height, label):
    self.x = x
    self.y = y
    self.width = width
    self.height = height
    self.label = label
    self.hover = False
    self.active = False

  def set_hover(self, value):
    self.hover = value
  
  def set_active(self, value):
    self.active = value

class ButtonView:
  NORMAL_COLOR = (100, 100, 100) # Light gray
  HOVER_COLOR = (150, 150, 150) # Gray
  ACTIVE_COLOR = (255, 0, 0) # Red
  TEXT_COLOR = (255, 255, 255) # White

  def __init__(self, font, text_size):
    self.font = font
    self.text_size = text_size

  def draw(self, screen, model):
    color = ButtonView.NORMAL_COLOR
    if model.active:
      color = ButtonView.ACTIVE_COLOR
    elif model.hover:
      color = ButtonView.HOVER_COLOR
    pygame.draw.rect(screen, color, (model.x, model.y, model.width, model.height))
    label = self.font.render(model.label, True, ButtonView.TEXT_COLOR)
    screen.blit(label, (model.x + model.width / 2 - label.get_rect().width / 2, model.y + model.height/2 - label.get_rect().height / 2))

class ButtonController:
  def __init__(self, model, view):
    self.model = model
    self.view = view

  def update(self, screen):
    self.view.draw(screen, self.model)

  def handle_mouse_move(self, x, y):
    hover = (self.model.x <= x <= self.model.x + self.model.width and
      self.model.y <= y <= self.model.y + self.model.height)
    self.model.set_hover(hover)

  def handle_click(self, x, y):
    if (self.model.x <= x <= self.model.x + self.model.width and
      self.model.y <= y <= self.model.y + self.model.height):
      self.model.set_active(True)
      return True
    return False

  def clear(self):
    self.model.set_active(False)

main()
