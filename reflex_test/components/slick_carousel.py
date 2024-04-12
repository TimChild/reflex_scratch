"""Reflex custom component Carousel."""

import reflex as rx

from reflex.utils import imports


# Some libraries you may want to wrap may require dynamic imports.
# This is because they they may not be compatible with Server-Side Rendering (SSR).
# To handle this in Reflex all you need to do is subclass NoSSRComponent instead.
# For example:
# from reflex.components.component import NoSSRComponent
# class Carousel(NoSSRComponent):
#     pass


class Carousel(rx.Component):
    """Carousel component."""

    # The React library to wrap.
    library = "react-slick"
    lib_dependencies: list[str] = ["slick-carousel"]

    # The React component tag.
    tag = "Slider"
    is_default = True

    autoplay: rx.Var[bool] = True
    autoplay_speed: rx.Var[int] = 3000
    pause_on_hover: rx.Var[bool] = True
    infinite: rx.Var[bool] = True
    lazy_load: rx.Var[bool] = True
    draggable: rx.Var[bool] = True
    center_mode: rx.Var[bool] = True
    center_padding: rx.Var[str] = "50px"
    slides_per_row: rx.Var[int] = 1
    easing: rx.Var[str] = "linear"
    as_nav_for: rx.Var[str] = None
    slide_handler: rx.Var[str] = None
    slides_to_show: rx.Var[int] = 1

    def _get_imports(self) -> imports.ImportDict:
        return imports.merge_imports(
            super()._get_imports(),
            {
                "": {
                    imports.ImportVar(
                        tag="slick-carousel/slick/slick.css",
                    ),
                    imports.ImportVar(
                        tag="slick-carousel/slick/slick-theme.css",
                    ),
                }
            },
        )

    # If the tag is the default export from the module, you can set is_default = True.
    # This is normally used when components don't have curly braces around them when importing.
    # is_default = True

    # If you are wrapping another components with the same tag as a component in your project
    # you can use aliases to differentiate between them and avoid naming conflicts.
    # alias = "OtherCarousel"

    # The props of the React component.
    # Note: when Reflex compiles the component to Javascript,
    # `snake_case` property names are automatically formatted as `camelCase`.
    # The prop names may be defined in `camelCase` as well.
    # some_prop: Var[str] = "some default value"
    # some_other_prop: Var[int] = 1

    # By default Reflex will install the library you have specified in the library property.
    # However, sometimes you may need to install other libraries to use a component.
    # In this case you can use the lib_dependencies property to specify other libraries to install.
    # lib_dependencies: list[str] = []

    # Event triggers, I did not understand the wording of the doc.
    # def get_event_triggers(self) -> dict[str, Any]:
    #     return {
    #         **super().get_event_triggers(),
    #         "on_change": lambda e0: [e0],
    #     }

    # To add custom code to your component
    # def _get_custom_code(self) -> str:
    #     return "const customCode = 'customCode';"


carousel = Carousel.create
