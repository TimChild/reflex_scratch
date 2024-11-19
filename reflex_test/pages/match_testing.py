import reflex as rx

from reflex_test.templates import template


class MatchState(rx.State):
    value: str

    def on_change(self, value: str):
        self.value = value


class SliderState(rx.State):
    value: int = 0

    def set_value(self, value: list[int | float]) -> None:
        self.value = int(value[0])


# MODEL_MAX_TOKENS = {
#     "gpt-3.5-turbo": 16000,
#     "gpt-4-turbo": 128000,
#     # TODO: 2024-05-01 -- rest...
#     "claude": 10000,
#     "command_r": 10000,
#     "gemini-1": 10000,
#     "gemini-1.5": 10000,
# }
MODEL_MAX_TOKENS = {
    "a": 10,
    "b": 100,
    "c": 1000,
    "d": 250,
}


def calc_max_value(current_model: str) -> rx.Var[int]:
    # return rx.match(1, (1, 10), 20)
    return rx.match(
        current_model,
        # ("gpt-3.5-turbo", 16000),
        *[(model, val) for model, val in MODEL_MAX_TOKENS.items()],
        10000,
    )


def get_match_str(current_model: str) -> rx.Var[str]:
    return rx.match(
        current_model,
        ("a", "10"),
        ("b", "s_100"),
        ("c", "s_1000"),
        ("d", "s_250"),
        "s_10000",
    )


class ExampleComponentState(rx.ComponentState):
    value: int = 100

    @classmethod
    def get_component(cls, match_value, *args, **kwargs):
        return rx.slider(
            on_value_commit=cls.set_value,
            default_value=cls.value,
            min=0,
            max=calc_max_value(match_value),
        )

    def set_value(self, value: list[int | float]) -> None:
        self.value = int(value[0])


@template(route="/match_testing", title="Match Testing")
def index():
    example_component = ExampleComponentState.create(match_value=MatchState.value)
    return rx.container(
        rx.vstack(
            rx.heading("Testing the rx.Match condition", size="5"),
            rx.divider(),
            rx.card(
                rx.select(
                    ["a", "b", "c", "d"],
                    default_value="a",
                    on_change=MatchState.on_change,
                ),
                rx.text(f"Value of MatchState.value: {MatchState.value}"),
                background_color=rx.color("orange", alpha=True),
            ),
            rx.divider(),
            rx.hstack(
                rx.card(
                    rx.heading("Matching to str to display rx.texts"),
                    rx.match(
                        MatchState.value,
                        ("a", rx.text("Matched a", color_scheme="yellow")),
                        ("b", rx.text("Matched b", color_scheme="red")),
                        ("c", rx.text("Matched c", color_scheme="green")),
                        ("d", rx.text("Matched d", color_scheme="blue")),
                    ),
                ),
            ),
            rx.divider(),
            rx.hstack(
                rx.card(
                    rx.heading("Matching to str to determine the color_scheme of rx.text"),
                    rx.text(
                        "Some text where color_scheme depends on match",
                        color_scheme=rx.match(
                            MatchState.value, ("a", "yellow"), ("b", "red"), ("c", "green"), ("d", "blue"), "purple"
                        ),
                    ),
                )
            ),
            rx.divider(),
            rx.hstack(
                rx.card(
                    rx.heading("Matching to str to determine background_color of rx.text"),
                    rx.text(
                        "Some text where background_color depends on match",
                        background_color=rx.match(
                            MatchState.value, ("a", "yellow"), ("b", "red"), ("c", "green"), ("d", "blue"), "purple"
                        ),
                    ),
                )
            ),
            rx.divider(),
            rx.hstack(
                rx.card(
                    rx.heading("Matching to str to determine max value of slider"),
                    rx.slider(
                        on_value_commit=SliderState.set_value,
                        default_value=SliderState.value,
                        min=0,
                        max=rx.match(
                            MatchState.value,
                            ("a", 10),
                            ("b", 100),
                            ("c", 1000),
                            ("d", 250),
                            3,
                        ),
                    ),
                    rx.text(f"Slider value is: {SliderState.value}"),
                )
            ),
            rx.divider(),
            rx.hstack(
                rx.card(
                    rx.heading("Using a function with rx.match to determine max value"),
                    rx.slider(
                        on_value_commit=SliderState.set_value,
                        default_value=SliderState.value,
                        min=0,
                        max=calc_max_value(MatchState.value),
                    ),
                    rx.text(f"Slider value is: {SliderState.value}"),
                )
            ),
            rx.divider(),
            rx.hstack(
                rx.card(
                    rx.heading("ComponentState with function rx.match to determine max value"),
                    example_component,
                    rx.text(f"ExampleComponentState.State.value is: {example_component.State.value}"),
                )
            ),
            rx.divider(),
            rx.hstack(
                rx.card(
                    rx.heading("Using rx.match to determine value within a string"),
                    rx.hstack(
                        rx.text("Calling the match as the only child of text: "),
                        rx.text(calc_max_value(MatchState.value)),
                    ),
                    # rx.text(f'Calling the match as part of fstring: {get_match_str(MatchState.value)}'),
                    rx.text("Calling the match as part of fstring: DOES NOT WORK"),
                    rx.text("Calling as second child of rx.text: ", calc_max_value(MatchState.value)),
                )
            ),
        ),
        padding_y="2em",
    )
