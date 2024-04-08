import reflex as rx

from ..components.basic_carousel import carousel as basic_carousel
from ..components.slick_carousel import carousel as slick_carousel
# from ..components.swiper_carousel import carousel as swiper_carousel
from ..templates import template


class CarouselState(rx.State):
    images = [
        "https://source.unsplash.com/random/800x600/?fruit",
        "https://source.unsplash.com/random/800x600/?nature",
        "https://source.unsplash.com/random/800x600/?night",
        "https://source.unsplash.com/random/800x600/?city",
    ]
    current_image = 0

    def next_image(self):
        self.current_image = (self.current_image + 1) % len(self.images)

    def prev_image(self):
        self.current_image = (self.current_image - 1) % len(self.images)
        

@template(route="/carousel", title="Carousel")
def index() -> rx.Component:
    return rx.container(
        basic_carousel(
            rx.foreach(CarouselState.images, lambda img: rx.image(src=img)),
        ),
        slick_carousel(
            rx.foreach(CarouselState.images, lambda img: rx.image(src=img)),
            id='primary-slick-carousel',
            # slides_per_row=2,
            # as_nav_for='secondary-slick-carousel',
        ),
        slick_carousel(
            rx.foreach(CarouselState.images, lambda img: rx.image(src=img)),
            id='secondary-slick-carousel',
            autoplay=False,
            # slides_per_row=4,
            slides_to_show=3,
            center_mode=True,
            center_padding='60px',
            # as_nav_for='primary-slick-carousel',
        ),
    )

