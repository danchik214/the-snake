from random import choice, randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (255, 255, 255)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет бомбы
BOMB_COLOR = (136, 69, 53)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption("Змейка")

# Настройка времени:
clock = pygame.time.Clock()


# Тут опишите все классы игры.
class GameObject:
    """Класс GameObject является основным родительским классом для других
    игровых классов.
    """

    position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    def __init__(self, position=None, body_color=None):
        if position is None:
            position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Метод для отрисовки объектов.
        В данном классе является заглушкой,
        для будущего переопределения в подклассах.
        """

        pass


class BoardItem(GameObject):
    """Класс BoardItem является общим родительским классом для объектов,
    по типу яблока и бомбы.
    """

    def __init__(self, position=None, body_color=None):
        super().__init__(position or (0, 0), body_color)
        if position is None:
            self.randomize_position()

    def randomize_position(self, forbidden=None):
        """Метод для случайного определения позиции на игровом поле."""

        forbidden = forbidden or []
        while True:
            new_pos = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
            if new_pos not in forbidden:
                self.position = new_pos
                break

    def draw(self):
        """Метод для отрисовки объектов на игровом поле."""

        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(BoardItem):
    """Класс служит для определения цвета яблока на игровом поле."""

    def __init__(self, position=None):
        super().__init__(position, APPLE_COLOR)


class Bomb(BoardItem):
    """Класс служит для определения цвета бомбы на игровом поле."""

    def __init__(self, position=None):
        super().__init__(position, BOMB_COLOR)


class Snake(GameObject):
    """Класс отвечает за объект 'Змейка' на игровом поле.
    Содержит в себе координаты начальной позиции змейки,
    длину змейки, направление движения, цвет.
    """

    possible_direction = [UP, DOWN, LEFT, RIGHT]

    def __init__(self, position=None, body_color=SNAKE_COLOR):
        if position is None:
            position = (0, 0)
        super().__init__(position, body_color)
        self.length = 1
        self.positions = [position]
        self.direction = RIGHT
        self.next_direction = None
        self.body_color = SNAKE_COLOR
        self.last_positions = []

    def get_head_position(self):
        """Метод для получения координат головы змейки."""

        return self.positions[0]

    def move(self):
        """Метод реализует свдиг змейки на одну ячейку."""

        head_x, head_y = self.get_head_position()
        dx, dy = self.direction

        new_position = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT,
        )

        self.positions.insert(0, new_position)
        if len(self.positions) > self.length:
            self.last_positions.append(self.positions.pop())

    def draw(self):
        """Метод для отрисовки змейки на игровом поле и
        затирания последнего сегмента змейки.
        """

        for position in self.positions[:-1]:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        for position in self.last_positions:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, rect)

        self.last_positions.clear()

    def shrink(self, amount=2):
        """Метод служит для сокращеия змейки."""

        if len(self.positions) <= 2:
            amount = 1

        self.length = max(1, self.length - amount)

        while len(self.positions) > self.length:
            self.last_positions.append(self.positions.pop())

    def reset(self):
        """Метод реализует очистку игрового поля и объектов."""

        screen.fill(BOARD_BACKGROUND_COLOR)
        self.length = 1
        self.positions = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = choice(self.possible_direction)
        self.next_direction = None
        self.last_positions.clear()

    def update_direction(self):
        """Метод обновления направления после нажатия на кнопку."""

        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None


def handle_keys(game_object):
    """Функция обработки действий пользователя."""

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_s and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_a and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_d and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    # Инициализация PyGame:
    pygame.init()
    # Тут нужно создать экземпляры классов.
    snake = Snake()
    apple = Apple()
    bomb = Bomb()

    apple.randomize_position(forbidden=snake.positions)
    bomb.randomize_position(forbidden=snake.positions + [apple.position])

    while True:
        clock.tick(SPEED)

        # Тут опишите основную логику игры.
        handle_keys(snake)
        snake.update_direction()
        snake.move()
        head = snake.get_head_position()
        if head == apple.position:
            snake.length += 1
            apple.randomize_position(
                forbidden=snake.positions + [bomb.position]
            )
        if head == bomb.position:
            snake.shrink(2)
            bomb.randomize_position(
                forbidden=snake.positions + [apple.position]
            )
        if head in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(
                forbidden=snake.positions + [bomb.position]
            )
            bomb.randomize_position(
                forbidden=snake.positions + [apple.position]
            )
        snake.draw()
        apple.draw()
        bomb.draw()
        pygame.display.update()


if __name__ == "__main__":
    main()
