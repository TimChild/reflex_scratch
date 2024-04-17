import reflex as rx


# @rx.page(route='/styling_test', title='Styling Test', description='Test of the styling')
# def index() -> rx.Component:
#     return rx.container(
#         rx.heading("Styling Test", size="5"),
#         rx.box(
#             rx.hstack(
#                 rx.heading("heading"),
#                 rx.text("text"),
#                 rx.link('link'),
#                 rx.text_area("text_area"),
#                 rx.input(default_value="input"),
#                 rx.moment(),
#                 rx.select(['opt 1', 'opt 2'], placeholder='select'),
#                 rx.button("button"),
#                 rx.card("card"),
#                 wrap='wrap',
#             ),
#             border="1px solid yellow",
#             font_size="1.5em",
#             color='orange',
#         )
#     )

@rx.page(route='/styling_test', title='Styling Test', description='Test of the styling')
def index() -> rx.Component:
    return rx.box(
        rx.box(
            rx.heading("Box that should change color on resize"),
            style=rx.style.Style(style_dict={
                'background_color': 'darkorchid',
                rx.style.media_query(3): {
                    'background_color': 'green'
                }
            }),
        ),
        rx.container(
            rx.heading("Box that should show smaller box on hover"),
            rx.box(
                rx.text("select by id"), position="absolute", top="10px", right=0, height="50%",
                id='inner-box',
                # _hover={'background_color': 'blue'},
                background_color="red",
            ),
            rx.box(
                rx.text("select by element"), rx.text("Also affects heading"), position="absolute", top="10px", right="100px", height="50%",
                background_color="red",
                transition='1s'
            ),
            rx.box(
                rx.text("select by class"), position="absolute", top="10px", right="400px", height="50%",
                background_color="red",
            ),
            position='relative', # So that absolute positioning in child works (without changing position of this)
            height="20vh",
            background_color="orange",
            style=rx.style.Style(style_dict={
                '&:hover': {
                    '#inner-box': {
                        'background_color': 'green',
                        'transition': '1s'
                    },
                    '.rt-Box': {
                        'background_color': 'purple',
                    },
                    'div': {
                        'background_color': 'blue',
                    },

                },
            }),
        ),
        border="1px solid yellow",

    )
