import turtle


class Snake:
    STARTING_POSITIONS = [(0, 0), (-20, 0), (-40, 0)]
    MOVE_DISTANCE = 20
    UP = 90
    DOWN = 270
    LEFT = 180
    RIGHT = 0

    def __init__(self, ):
        self.snake = []
        self.set_body()
        self.head = self.snake[0]

    def set_body(self):
        for pos in self.STARTING_POSITIONS:
            snake_body_part = turtle.Turtle("square")
            snake_body_part.penup()
            snake_body_part.color('white')
            snake_body_part.goto(pos)
            self.snake.append(snake_body_part)

    def move(self):
        for idx in range(len(self.snake) - 1, 0, -1):
            x = self.snake[idx - 1].xcor()
            y = self.snake[idx - 1].ycor()
            self.snake[idx].goto(x, y)
        self.snake[0].forward(self.MOVE_DISTANCE)

    def up(self):
        if self.head.heading() != self.DOWN:
            self.head.setheading(self.UP)

    def down(self):
        if self.head.heading() != self.UP:
            self.head.setheading(self.DOWN)

    def left(self):
        if self.head.heading() != self.RIGHT:
            self.head.setheading(self.LEFT)

    def right(self):
        if self.head.heading() != self.LEFT:
            self.head.setheading(self.RIGHT)
