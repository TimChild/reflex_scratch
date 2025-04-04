# from .settings import settings
from .main_app import main_app
from .payments_page import index as payments_page
from .cookie_test import index as cookie_test

from .drawer_select_issue import index as drawer_select_issue

# from .chatroom import chatroom
# from .webcam import index as webcam
# from .audio_record import index as audio_record
# from .audio_recorder_2 import index as audio_recorder_2
from .audio_recorder_polyfill import index as audio_recorder_polyfill

# from .carousel import index as carousel
from .scroll_area_width_issue import index as scroll_area_width_issue
from .component_with_state import index as component_with_state
from .async_background_testing import index as async_background_testing

# from ..reflex_issues.textarea_set_value_thought import index as textarea_set_value_thought
# from .stripe_payment_element import index as stripe_payment_element
# from .scroll_snap_testing import index as scroll_snap_testing
# from .styling_test import index as styling_test
# from .regular_python_in_frontend_example import index as regular_python_in_frontend_example
from .select_with_id_testing import index as select_with_id_testing
from .components_and_states_testing import index as components_and_states_testing

# from .pydantic_v2_to_base import index as pydantic_v2_to_base
from .dynamic_update_text_area import index as dynamic_update_text_area
from .stateful_component import index as stateful_component
from .match_testing import index as match_testing
from .set_value_testing import index as set_value_testing
from .nested_states_example import index as nested_states_example
from .using_values_in_rx_base import index as using_values_in_rx_base
from .component_state_in_foreach_issue import index as component_state_in_foreach_issue
from .redis_mixin_testing import index as redis_mixin_testing
from .mixin_cached_or_background_issue import index as mixin_cached_or_background_issue
from .separation_of_display_from_processing import index as separation_of_display_from_processing
from .async_cached_var_issue import index as async_cached_var_issue
from .inherit_multiple_mixin import index as inherit_multiple_mixin

# from .pydantic_v2_test import index as pydantic_v2_test
from .updating_vars_with_unrelated_state_self import index as updating_vars_with_unrelated_state_self
from .counter_example import index as counter_example
from .markdown_with_copy import index as markdown_with_copy
from .multi_checkbox import index as multi_checkbox
from .textarea_expand_script import index as textarea_expand
from .duplicate_tabs_issue import index as duplicate_tabs_issue


# from .match_in_fstring_issue import index as match_in_fstring_issue

__all__ = [
    # "settings",
    "main_app",
    "cookie_test",
    # "chatroom",
    # "webcam",
    # "audio_record",
    "audio_recorder_polyfill",
    # "carousel",
    "duplicate_tabs_issue",
    "scroll_area_width_issue",
    "component_with_state",
    "async_background_testing",
    # "audio_recorder_2",
    # "textarea_set_value_thought",
    # "stripe_payment_element",
    # "scroll_snap_testing",
    # "styling_test",
    # "regular_python_in_frontend_example",
    "select_with_id_testing",
    "components_and_states_testing",
    # "pydantic_v2_to_base",
    "dynamic_update_text_area",
    "stateful_component",
    "match_testing",
    "set_value_testing",
    "nested_states_example",
    "using_values_in_rx_base",
    "component_state_in_foreach_issue",
    "redis_mixin_testing",
    "mixin_cached_or_background_issue",
    "separation_of_display_from_processing",
    "async_cached_var_issue",
    "inherit_multiple_mixin",
    #
    # "match_in_fstring_issue",
    # "pydantic_v2_test",
    "updating_vars_with_unrelated_state_self",
    "counter_example",
    "markdown_with_copy",
    "multi_checkbox",
    "textarea_expand",
    "drawer_select_issue",
    "payments_page",
]
