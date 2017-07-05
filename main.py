import itertools
import pytmx
from kivy import Config
from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, \
    ObjectProperty, Clock, Logger
from kivy.vector import Vector
import tiled
from kivy.core.image import Image as CoreImage



class PongPaddle(Widget):
    score = NumericProperty(0)

    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            vx, vy = ball.velocity
            offset = (ball.center_y - self.center_y) / (self.height / 2)
            bounced = Vector(-1 * vx, vy)
            vel = bounced * 1.1
            ball.velocity = vel.x, vel.y + offset


class PongBall(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos


class TileSet(Widget):
    tmxdata = pytmx.TiledMap("data/Map/test01.tmx")
    image = tmxdata.get_tile_image(0, 0, 0)
    def test(self):
        pass

class PongGame(Widget):
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)

    def image(self, path, colorkey, tileset):
        Config.set("kivy", "log_level", "debug")
        tile_image_path = "data/Map" + '/' + tileset.source
        print(tile_image_path)
        Logger.debug('KivyTiledMap: loading tile image at {}'.format(tile_image_path))
        Image(source=tile_image_path)
        texture = CoreImage(tile_image_path).texture

        tileset.width, tileset.height = texture.size
        tilewidth = tileset.tilewidth + tileset.spacing
        tileheight = tileset.tileheight + tileset.spacing
        Logger.debug('KivyTiledMap: TiledTileSet: {}x{} with {}x{} tiles'.format(tileset.width, tileset.height, tilewidth, tileheight))

        # some tileset images may be slightly larger than the tile area
        # ie: may include a banner, copyright, ect.  this compensates for that
        width = int((((tileset.width - tileset.margin * 2 + tileset.spacing) / tilewidth) * tilewidth) - tileset.spacing)
        height = int((((tileset.height - tileset.margin * 2 + tileset.spacing) / tileheight) * tileheight) - tileset.spacing)
        Logger.debug('KivyTiledMap: TiledTileSet: true size: {}x{}'.format(width, height))

        # initialize the image array
        Logger.debug('KivyTiledMap: initializing image array')
        self.images = [0] * 100

        p = itertools.product(
            range(tileset.margin, height + tileset.margin, tileheight),
            range(tileset.margin, width + tileset.margin, tilewidth)
        )

        # trim off any pixels on the right side that isn't a tile
        # this happens if extra graphics are included on the left, but they are not actually part of the tileset
        width -= (tileset.width - tileset.margin) % tilewidth

        for real_gid, (y, x) in enumerate(p, tileset.firstgid):
            if x + tileset.tilewidth - tileset.spacing > width:
                continue

            gids = self.map_gid(real_gid)

            if gids:
                # invert y for OpenGL coordinates
                y = tileset.height - y - tileset.tileheight

                tile = texture.get_region(x, y, tileset.tilewidth, tileset.tileheight)

                for gid, flags in gids:
                    self.images[gid] = tile

    def serve_ball(self, vel=(4, 0)):
        self.ball.center = self.center
        self.ball.velocity = vel

        tmx_data= pytmx.TiledMap("data/Map/test01.tmx", self.image)
        print(tmx_data.get_tile_properties(0,0,0))

        tmx_data.get_tile_image(0, 0, 0)



    def update(self, dt):
        self.ball.move()

        # bounce of paddles
        self.player1.bounce_ball(self.ball)
        self.player2.bounce_ball(self.ball)

        # bounce ball off bottom or top
        if (self.ball.y < self.y) or (self.ball.top > self.top):
            self.ball.velocity_y *= -1

        # went of to a side to score point?
        if self.ball.x < self.x:
            self.player2.score += 1
            self.serve_ball(vel=(4, 0))
        if self.ball.x > self.width:
            self.player1.score += 1
            self.serve_ball(vel=(-4, 0))

    def on_touch_move(self, touch):
        if touch.x < self.width / 3:
            self.player1.center_y = touch.y
        if touch.x > self.width - self.width / 3:
            self.player2.center_y = touch.y


class PongApp(App):
    def build(self):
        game = PongGame()
        game.serve_ball()

        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game


if __name__ == '__main__':
    PongApp().run()