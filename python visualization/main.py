import pygame
import sys
import random
import heapq
from sortedcontainers import SortedList

# Constants
WIDTH, HEIGHT = 1400, 900
# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GREY = (200, 200, 200)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Define Point and Segment classes
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"({self.x}, {self.y})"

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

class Segment:
    def __init__(self, p1, p2, name):
        if p1.x > p2.x:  # Ensure p1 is the left endpoint
            p1, p2 = p2, p1
        self.p1 = p1
        self.p2 = p2
        self.name = name  # Helpful for debugging

    # Slope of the line
    def slope(self):
        if self.p1.x == self.p2.x:
            return float('inf')
        return (self.p2.y - self.p1.y) / (self.p2.x - self.p1.x)

    # Y Intercept of the line
    def y_intercept(self):
        return self.p1.y - self.slope() * self.p1.x

    # Value at x
    def value_at(self, x):
        return self.slope() * x + self.y_intercept()
    
    # String representation of the segment
    def __repr__(self):
        return f"{self.name}: ({self.p1.x}, {self.p1.y}) to ({self.p2.x}, {self.p2.y})"

class Event:
    def __init__(self, point, segment1, type, segment2=None):
        self.point = point
        self.segment1 = segment1
        self.type = type  # 'left', 'right', or 'cross'
        self.segment2 = segment2

    def __lt__(self, other):
        if self.point.x != other.point.x:
            return self.point.x < other.point.x
        if self.type != other.type:
            # Prioritize 'left' events over 'right' and 'cross' events
            return self.type == 'left'
        # If events have the same x coordinate and type, use y coordinate
        return self.point.y < other.point.y

    def __repr__(self):
        return f"Event({self.point}, {self.type})"


# Model
class LineSweepAlgorithmModel:
    def __init__(self):
        # Current position of the sweep line
        self.sweep_x = 0
        # A list of all segments
        self.segments = []
        # A list of all events
        self.events_queue = []
        # Priority queue of events using heapq
        heapq.heapify(self.events_queue)  # Heapify once when creating the queue
        # Balanced binary search tree of segments that sorts by the Y value of the segment at the current position of the sweep line
        self.active_segments = SortedList(key=lambda segment: segment.value_at(self.sweep_x))

        # This is the active point that is being dragged
        self.selected_point = None

        # Styling for the box
        self.box_margin = 10
        # Adjusted box dimensions
        box_width = min(WIDTH - 2 * self.box_margin, HEIGHT - self.box_margin - 300)
        self.box = pygame.Rect(self.box_margin, self.box_margin, box_width, box_width)
        self.sweep_x = 0  # X-coordinate of the sweep line
        self.sweeping = False  # Flag to control the sweeping action

    # Get list of events
    def get_events_queue(self):
        heapq.heapify(self.events_queue)
        events = heapq.nsmallest(len(self.events_queue), self.events_queue)
        return events

    # Function to print the events queue
    def print_events_queue(self):
        events = self.get_events_queue()
        for event in events:
            print(event)

    def add_internal(self, start, end):
        # Create the segment object
        new_segment = Segment(start, end, "S" + str(len(self.segments) + 1))

        # Create the event objects
        left_event = Event(new_segment.p1, new_segment, 'left')
        right_event = Event(new_segment.p2, new_segment, 'right')

        # Add the events to the queue
        heapq.heappush(self.events_queue, left_event)
        heapq.heappush(self.events_queue, right_event)

        # Add the segment to the list
        self.segments.append(new_segment)

        print("Events Queue")
        self.print_events_queue()

    # Add a new segment
    def add_segment_to_event_queue(self):
        # Create the segment with random points
        start = Point(random.randint(self.box.left, self.box.right),
                      random.randint(self.box.top, self.box.bottom))
        end = Point(random.randint(self.box.left, self.box.right),
                    random.randint(self.box.top, self.box.bottom))
        # Create the segment object
        new_segment = Segment(start, end, "S" + str(len(self.segments) + 1))

        # Create the event objects
        left_event = Event(new_segment.p1, new_segment, 'left')
        right_event = Event(new_segment.p2, new_segment, 'right')

        # Add the events to the queue
        heapq.heappush(self.events_queue, left_event)
        heapq.heappush(self.events_queue, right_event)

        # Add the segment to the list
        self.segments.append(new_segment)

        print("Events Queue")
        self.print_events_queue()

    # Delete the most recent segment and remove its events
    def delete_segment_from_event_queue(self):
        if self.segments:
            segment = self.segments.pop()
            # List of events to remove
            events_to_remove = []
            for event in self.events_queue:
                if event.segment1 == segment:
                    events_to_remove.append(event)
            for event in events_to_remove:
                self.events_queue.remove(event)
            print("Events Queue")
            self.print_events_queue()
    
    # Pop event from priority queue and handle it
    def pop_event(self):
        # Handle empty events queue
        if not self.events_queue:
            return
        # Pop the event from the priority queue
        event = heapq.heappop(self.events_queue)
        
        # Update the sweep line position to the event point's x-coordinate
        self.sweep_x = event.point.x

        # Handle the event
        if event.type == 'left':
            self.handle_left_event(event)
        elif event.type == 'right':
            self.handle_right_event(event)
        elif event.type == 'cross':
            self.handle_cross_event(event)

    
    # Simplified Intersection Check
    def calculate_intersection(self, a, b):
        # If the segments are parallel, they don't intersect
        if a is None or b is None or a.slope() == b.slope():
            return None
        
        # Calculate the intersection point
        x_intersect = (a.y_intercept() - b.y_intercept()) / (b.slope() - a.slope())
        a_range = (min(a.p1.x, a.p2.x), max(a.p1.x, a.p2.x))
        b_range = (min(b.p1.x, b.p2.x), max(b.p1.x, b.p2.x))

        # Check if the intersection point is within the range of the segments
        if x_intersect < a_range[0] or x_intersect > a_range[1] or x_intersect < b_range[0] or x_intersect > b_range[1]:
            return None

        # Calculate the y value at the intersection point
        intersection_y = a.value_at(x_intersect)

        # Return the intersection point
        return Point(round(x_intersect), round(intersection_y))

    # Handling Left Event
    def handle_left_event(self, event):
        segment = event.segment1
        self.active_segments.add(segment)
        index = self.active_segments.index(segment)
        neighbors = []

        if index > 0:
            neighbors.append(self.active_segments[index - 1])
        if index < len(self.active_segments) - 1:
            neighbors.append(self.active_segments[index + 1])

        for neighbor in neighbors:
            intersection_point = self.calculate_intersection(segment, neighbor)
            if intersection_point:
                cross_event = Event(intersection_point, segment, 'cross', neighbor)
                heapq.heappush(self.events_queue, cross_event)

    # Handling Right Event
    def handle_right_event(self, event):
        segment = event.segment1
        if segment in self.active_segments:  # Check if segment is actually active before trying to remove it
            index = self.active_segments.index(segment)
            above = None
            below = None

            if index > 0:
                above = self.active_segments[index - 1]
            if index < len(self.active_segments) - 1:
                below = self.active_segments[index + 1]

            self.active_segments.remove(segment)

            if above and below:
                intersection_point = self.calculate_intersection(above, below)
                if intersection_point:
                    cross_event = Event(intersection_point, above, 'cross', below)
                    heapq.heappush(self.events_queue, cross_event)
        else:
            print(f"Attempted to remove segment not in active list: {segment}")

    # Handling Cross Event
    def handle_cross_event(self, event):
        segment1, segment2 = event.segment1, event.segment2

        # Check both segments exist in the list before proceeding
        if segment1 in self.active_segments and segment2 in self.active_segments:
            index1 = self.active_segments.index(segment1)
            index2 = self.active_segments.index(segment2)
            
            # Swap positions to handle the cross
            self.active_segments[index1], self.active_segments[index2] = self.active_segments[index2], self.active_segments[index1]

            # After handling the cross event, check for new potential intersections
            for segment, other_segment in [(segment1, segment2), (segment2, segment1)]:
                index = self.active_segments.index(segment)
                neighbors = []

                if index > 0:
                    neighbors.append(self.active_segments[index - 1])
                if index < len(self.active_segments) - 1:
                    neighbors.append(self.active_segments[index + 1])

                for neighbor in neighbors:
                    intersection_point = self.calculate_intersection(segment, neighbor)
                    if intersection_point:
                        cross_event = Event(intersection_point, segment, 'cross', neighbor)
                        heapq.heappush(self.events_queue, cross_event)
        else:
            print(f"One or both segments not in active list at cross event: {segment1}, {segment2}")



# View
class LineSweepAlgorithmView:
    def __init__(self, screen):
        self.screen = screen
        self.FONT = pygame.font.Font(None, 36)
        self.events_list_y = 10
        self.events_list_x = 620
        self.segments_list_y = 10
        self.segments_list_x = 900

    def draw(self, segments):
        for segment in segments:
            pygame.draw.aaline(self.screen, BLACK, (segment.p1.x, segment.p1.y),
                               (segment.p2.x, segment.p2.y), 5)
            pygame.draw.circle(self.screen, GREEN, (segment.p1.x, segment.p1.y), 6)
            pygame.draw.circle(self.screen, BLUE, (segment.p2.x, segment.p2.y), 6)

    def draw_boundaries(self, box):
        pygame.draw.rect(self.screen, BLACK, box, 2)

    def draw_sweep_line(self, sweep_x, box, delay=0):
        if sweep_x > 0:  # Only draw if sweep has started
            y_step = 10
            for y in range(box.top, box.bottom, 2 * y_step):
                # slow down the sweep line
                if delay > 0:
                    pygame.time.delay(delay)
                pygame.draw.line(self.screen, BLACK, (sweep_x, y), (sweep_x, y + y_step), 1)

    def display_events_queue(self, events):
        start_y = self.events_list_y
        # Write the words "Events Queue"
        text_surface = self.FONT.render("Events Queue:", True, BLACK)
        self.screen.blit(text_surface, (self.events_list_x, start_y))
        start_y += 30  # Increment y position for next event
        for event in events:
            text_surface = self.FONT.render(str(event), True, BLACK)
            self.screen.blit(text_surface, (self.events_list_x, start_y))
            start_y += 30  # Increment y position for next event
    
    def display_segments_list(self, segments):
        start_y = self.segments_list_y
        # Write the words "Segments List"
        text_surface = self.FONT.render("Segments List:", True, BLACK)
        self.screen.blit(text_surface, (self.segments_list_x, start_y))
        start_y += 30
        for segment in segments:
            text_surface = self.FONT.render(str(segment), True, BLACK)
            self.screen.blit(text_surface, (self.segments_list_x, start_y))
            start_y += 30

    def draw_buttons(self, buttons):
        for button in buttons:
            button.draw(self.screen)
    
    def display_active_segments(self, active_segments):
        start_y = 600  # Start position on screen for active segments
        text_surface = self.FONT.render("Active Segments:", True, BLACK)
        self.screen.blit(text_surface, (self.segments_list_x, start_y))
        start_y += 30
        for segment in active_segments:
            text_surface = self.FONT.render(str(segment), True, BLACK)
            self.screen.blit(text_surface, (self.segments_list_x, start_y))
            start_y += 30


class Button:
    def __init__(self, rect, text, font, color, action):
        self.rect = rect
        self.text = text
        self.font = font
        self.color = color
        self.action = action

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=5)
        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def clicked(self, pos):
        if self.rect.collidepoint(pos):
            self.action()

# Controller
class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        button_font = pygame.font.Font(None, 36)
        button_color = LIGHT_GREY
        self.buttons = [
            Button(pygame.Rect(50, HEIGHT - 100, 50, 50), '+', button_font, button_color, self.model.add_segment_to_event_queue),
            Button(pygame.Rect(105, HEIGHT - 100, 50, 50), '-', button_font, button_color, self.model.delete_segment_from_event_queue),
            Button(pygame.Rect(310, HEIGHT - 100, 70, 50), 'Step', button_font, button_color, self.model.pop_event),
            Button(pygame.Rect(390, HEIGHT - 100, 100, 50), 'Reset', button_font, button_color, self.reset)
        ]


    def reset(self):
        temp = self.model.segments.copy()
        self.model.segments = []
        self.model.events_queue = []
        self.model.active_segments.clear()
        self.model.sweep_x = 0 

        for segment in temp:
            self.model.add_internal(segment.p1, segment.p2)


    def start_line_sweep(self):
        self.model.sweeping = True
        self.model.sweep_x = self.model.box.left

    def stop_line_sweep(self):
        self.model.sweeping = False

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for button in self.buttons:
                button.clicked(event.pos)

            for segment in self.model.segments:
                if pygame.Rect(segment.p1.x - 6, segment.p1.y - 6, 12, 12).collidepoint(event.pos):
                    self.model.selected_point = segment.p1
                elif pygame.Rect(segment.p2.x - 6, segment.p2.y - 6, 12, 12).collidepoint(event.pos):
                    self.model.selected_point = segment.p2

        elif event.type == pygame.MOUSEBUTTONUP:
            self.model.selected_point = None

        elif event.type == pygame.MOUSEMOTION and self.model.selected_point:
            # Create a new segment
            new_x = max(self.model.box.left, min(event.pos[0], self.model.box.right))
            new_y = max(self.model.box.top, min(event.pos[1], self.model.box.bottom))

            self.model.selected_point.x, self.model.selected_point.y = new_x, new_y

def main():
    # Initialize Pygame
    pygame.init()

    # Set up the display
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Line Sweep Intersection")

    # Setup MVC components
    model = LineSweepAlgorithmModel()
    view = LineSweepAlgorithmView(screen)  # Pass the screen object to the view
    controller = Controller(model, view)

    # Main loop
    running = True
    while running:
        screen.fill(WHITE)  # Clear the screen
        view.draw_boundaries(model.box)
        view.draw_buttons(controller.buttons)
        view.draw(model.segments)
        view.draw_sweep_line(model.sweep_x, model.box)
        view.display_events_queue(model.get_events_queue())
        view.display_segments_list(model.segments)
        view.display_active_segments(model.active_segments)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            controller.handle_events(event)

        pygame.display.flip()  # Update the display


    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
