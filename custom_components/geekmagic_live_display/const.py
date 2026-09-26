"""Constants for GeekMagic Live Display."""

DOMAIN = "geekmagic_live_display"

SERVICE_SHOW = "show"
SERVICE_SHOW_ENTITIES = "show_entities"
SERVICE_WATCH_ENTITIES = "watch_entities"
SERVICE_STOP_WATCHING = "stop_watching"

ATTR_BACKGROUND_COLOR = "background_color"
ATTR_ENTRY_ID = "entry_id"
ATTR_ENTITY_ID = "entity_id"
ATTR_FOREGROUND_COLOR = "foreground_color"
ATTR_MESSAGE = "message"
ATTR_TITLE = "title"

DATA_CLIENTS = "clients"
DATA_WATCHERS = "watchers"

ATTR_TOTAL_SPACE = "total_space"

DEFAULT_BACKGROUND_COLOR = "#101820"
DEFAULT_FOREGROUND_COLOR = "#f2aa4c"

DISPLAY_SIZE = 240
LIVE_IMAGE_NAME = "home_assistant_live.jpg"
PHOTO_THEME = "3"

THEMES = {
    "1": "Weather Clock Today",
    "2": "Weather Forecast",
    "3": "Photo Album",
    "4": "Time Style 1",
    "5": "Time Style 2",
    "6": "Time Style 3",
    "7": "Simple Weather Clock",
}
