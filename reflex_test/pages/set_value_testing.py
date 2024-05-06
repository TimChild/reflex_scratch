import reflex as rx

from reflex_test.templates import template


@template(route='/set_value_testing', title='set_value Testing')
def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.heading('Testing the rx.set_value event', size="5"),
            rx.divider(),
            rx.input(id='input_id'),
            rx.button('reset input', on_click=rx.set_value('input_id', 'something')),
            rx.divider(),
            rx.text_area(id='text_area_id'),
            rx.button('reset text_area', on_click=rx.set_value('text_area_id', 'something else')),
            rx.divider(),
            rx.slider(id='slider_id', min=0, max=100, default_value=50),
            rx.button('reset slider', on_click=rx.set_value('slider_id', 25)),
            rx.text("Doesn't work for slider"),
            rx.divider(),
            rx.select(['a', 'b', 'c'], id='select_id', default_value='b'),
            rx.button('reset select', on_click=rx.set_value('select_id', 'a')),
            rx.text("Doesn't work for select"),
            rx.divider(),
        ),
        padding="2em",
    )