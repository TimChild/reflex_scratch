"""Swiper custom component Carousel.

2024-04-06

Not sure how to implement this one... wants me to use `element` instead of `react`, and then I get lost...
"""
from typing import Any

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
    library = "swiper"
    # lib_dependencies: list[str] = ["swiper/css"]

    # The React component tag.
    tag = "Swiper"
    is_default = False

    autoplay: rx.Var[Any] = True  # bool or autoplay parameters (e.g. {delay: 5000})
    centered_slides: rx.Var[bool] = True

    def _get_imports(self) -> imports.ImportDict:
        return imports.merge_imports(
            super()._get_imports(),
            {
                "": {
                    imports.ImportVar(
                        tag="swiper/css",
                    ),
                    imports.ImportVar(
                        tag="swiper/css/navigation",
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
