import reflex as rx


@rx.page('/')
def index():
    return rx.text(f'Error with match as part of fstring: {rx.match("a", ("a", "Matched a"), "b").to_string()}')
    # return rx.text(f'No error if outside fstring: ', rx.match("a", ("a", "Matched a"), "b"))

