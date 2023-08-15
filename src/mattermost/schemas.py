from enum import StrEnum

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl, model_validator

from .services import get_root_url


class Permission(StrEnum):
    """Разрешения приложения"""
    act_as_bot = 'act_as_bot'
    act_as_user = 'act_as_user'
    remote_oauth2 = 'remote_oauth2'
    remote_webhooks = 'remote_webhooks'


class Location(StrEnum):
    """Места в интерфейсе Mattermost, к которым есть доступ у приложения"""
    post_menu = '/post_menu'
    channel_header = '/channel_header'
    command = '/command'
    in_post = '/in_post'


class ExpandLevel(StrEnum):
    """Кол-во информации, включенной в метаданные вызова"""
    none = 'none'
    all = 'all'  # noqa: A003
    summary = 'summary'
    id = 'id'  # noqa: A003


class FormFieldType(StrEnum):
    """Тип поля формы"""
    text = 'text'
    static_select = 'static_select'
    dynamic_select = 'dynamic_select'
    bool = 'bool'  # noqa: A003
    user = 'user'
    channel = 'channel'
    markdown = 'markdown'


class TextFieldSubtype(StrEnum):
    """Тип текстового поля"""
    input = 'input'  # A single-line text input field  # noqa: A003
    textarea = 'textarea'  # A multi-line text input field; uses the HTML textarea element
    email = 'email'  # A field for editing an email address
    number = 'number'  # A field for entering a number; includes a spinner component
    password = 'password'  # A single-line text input field whose value is obscured  # noqa: S105
    tel = 'tel'  # A field for entering a telephone number
    url = 'url'  # A field for entering a URL


class Expand(BaseModel):
    """Метаданные вызова"""
    app: ExpandLevel | None = Field(default=None, title='Expands the app information')
    acting_user: ExpandLevel | None = Field(default=None, title='Expands the acting user information')
    acting_user_access_token: ExpandLevel | None = Field(default=None, title='Include the user-level access token')
    locale: ExpandLevel | None = Field(default=None, title='Expands the user locale, to be used in localizations')
    channel: ExpandLevel | None = Field(default=None, title='Expands the channel information')
    channel_member: ExpandLevel | None = Field(default=None, title='Expands channel member information')
    team: ExpandLevel | None = Field(default=None, title='Expands the team information')
    team_member: ExpandLevel | None = Field(default=None, title='Expands team member information')
    post: ExpandLevel | None = Field(default=None, title='Expands the post information')
    root_post: ExpandLevel | None = Field(default=None, title='Expands the root post information')
    user: ExpandLevel | None = Field(default=None, title='Expands the subject user information')
    oauth2_app: ExpandLevel | None = Field(default=None, title='Expands the remote OAuth2 configuration data')
    oauth2_user: ExpandLevel | None = Field(default=None, title='Expands the remote OAuth2 user data')


class Call(BaseModel):
    """Методы и вызовы приложения"""
    path: str = Field(
        title='The path of the call',
        description='For Apps deployed using HTTP, the path is appended to the App’s RootURL'
    )
    expand: Expand | None = Field(
        default=None,
        title='Specifies additional metadata to include in the call request, such as channel and post information'
    )
    state: dict | None = Field(
        default=None,
        title='A set of elements to be interpreted by the App',
        description='Forms and slash commands will also populate these values'
    )


class Http(BaseModel):
    """Конфигурация доступа к приложению через HTTP"""
    root_url: HttpUrl = Field(
        default=get_root_url(),
        title='Base URL for all calls and static asset requests'
    )
    use_jwt: bool = Field(
        default=False,
        title='Include a secret-based JWT in all requests to the App',
        description='The secret must be provided by the App to the System Admin and entered when the App is installed'
    )


class Manifest(BaseModel):
    """Манифест приложения"""
    app_id: str = Field(default='matterlab', title='ID for your App')
    homepage_url: HttpUrl = Field(
        default='https://gitlab.com/creonit/matterlab',
        title='The App homepage',
        description='Used in the Marketplace and for OAuth purposes'
    )
    version: str | None = Field(default='v0.0.1', title='The version of your App')
    display_name: str = Field(default='Matterlab', title='The display name for your App')
    description: str | None = Field(
        default=None,
        title='The description for your App',
        description='Used in the product Marketplace. '
                    'Provide examples of key functionality the App provides in a short paragraph'
    )
    icon: str | None = Field(
        default=None,
        title='The icon for your App',
        description='Must be a relative path to a PNG image in the static assets folder. '
                    'Used as the bot account icon and in the product Marketplace.'
    )
    requested_permissions: list[Permission] | None = Field(
        default=[Permission.act_as_bot, Permission.act_as_user],
        title='List of permissions needed by the App'
    )
    requested_locations: list[Location] | None = Field(
        default=[Location.channel_header, Location.command],
        title='The list of top-level locations that the App intends to bind to'
    )
    bindings: Call | None = Field(
        default=None,
        title='The call invoked to retrieve bindings',
        description='Default value: /bindings'
    )
    on_install: Call | None = Field(
        default=None,
        title='The call invoked when the App is installed'
    )
    on_uninstall: Call | None = Field(
        default=None,
        title='The call invoked when the App is uninstalled, before the App is removed'
    )
    on_version_changed: Call | None = Field(
        default=None,
        title='The call invoked when the App needs to be upgraded or downgraded'
    )
    get_oauth2_connect_url: Call | None = Field(
        default=None,
        title='The call invoked when an OAuth2 authentication flow has started'
    )
    on_oauth2_complete: Call | None = Field(
        default=None,
        title='The call invoked when an OAuth2 authentication flow has successfully completed'
    )
    on_remote_webhook: Call | None = Field(
        default=None,
        title='The call invoked when an App webhook is received from a remote system'
    )
    remote_webhook_auth_type: str | None = Field(
        default=None,
        title='Specifies how incoming App webhook messages from remote systems should be authenticated by Mattermost',
        description='One of "", none, or secret. Default value: "". '
                    'The value "" is treated as if it were the value secret'
    )
    http: Http = Field(
        default=Http(),
        title='Metadata for an App that is already deployed externally and is accessed using HTTP'
    )


class Select(BaseModel):
    """Варианты ответов для поля static_select"""
    label: str = Field(title='User-facing string', description='Defaults to value and must be unique on this field')
    value: str = Field(title='Machine-facing value', description='Must be unique on this field')
    icon_data: str | None = Field(
        default=None,
        title='Either a fully-qualified URL, or a path for an app’s static asset'
    )


class FormField(BaseModel):
    """Поле формы"""
    name: str = Field(title='Key to use in the values field of the call', description='Cannot include spaces or tabs')
    type_: FormFieldType = Field(title='The type of the field', alias='type')
    is_required: bool = Field(default=False, title='Whether the field has a mandatory value')
    readonly: bool = Field(default=False, title='Whether a field’s value is read-only')
    value: str | int | bool | None = Field(default=None, title='The field’s default value')
    description: str | None = Field(
        default=None,
        title='Short description of the field, displayed beneath the field in modal dialogs'
    )
    label: str | None = Field(
        default=None,
        title='The label of the flag parameter',
        description='Used with autocomplete. Ignored for positional parameters'
    )
    hint: str | None = Field(
        default=None,
        title='The hint text for the field'
    )
    position: int | None = Field(
        default=None,
        title='The index of the positional argument',
        description='A value greater than zero indicates the position this field is in. '
                    'A value of -1 indicates the last argument'
    )
    multiselect: bool | None = Field(
        default=False,
        title='Whether a select field allows multiple values to be selected'
    )
    modal_label: str | None = Field(
        default=None,
        title='Label of the field in modal dialogs',
        description='Defaults to label if not defined'
    )
    refresh: bool | None = Field(
        default=None,
        title='Allows the form to be refreshed when the value of the field has changed'
    )
    options: list[Select] | None = Field(default=None, title='A list of options for static select fields')
    lookup: Call | None = Field(default=None, title='A call that returns a list of options for dynamic select fields')
    subtype: TextFieldSubtype | None = Field(default='', title='The subtype of text field that will be shown')
    min_length: int | None = Field(default=None, title='The minimum length of text field input')
    max_length: int | None = Field(default=None, title='The maximum length of text field input')


class Form(BaseModel):
    """Форма"""
    title: str = Field(title='Title of the form, shown in modal dialogs')
    submit: Call = Field(title='Call to perform when the form is submitted or the slash command is executed')
    fields: list[FormField] = Field(title='List of fields in the form')
    source: Call | None = Field(
        default=None,
        title='Call to perform when a form’s fields are not defined or when the form needs to be refreshed'
    )
    header: str | None = Field(default=None, title='Text used as introduction in modal dialogs')
    footer: str | None = Field(default=None, title='Text used at the end of modal dialogs')
    icon: str | None = Field(
        default=None,
        title='Either a fully-qualified URL, or a path for an app’s static asset'
    )


class Binding(BaseModel):
    """Данные о привязках к командам"""
    location: str | None = Field(
        default=None,
        title='The name of the binding location',
        description='Values must be unique within each top level binding'
    )
    icon: str | None = Field(
        default=None,
        title='The App icon to display',
        description='Either a fully-qualified URL or a path to an App static asset. Required for web app support'
    )
    label: str | None = Field(
        default=None,
        title='The primary text to display at the binding location',
        description='Defaults to the value of the location field'
    )
    hint: str | None = Field(
        default=None,
        title='Secondary text to display at the binding location'
    )
    description: str | None = Field(
        default=None,
        title='Extended help text used in modal forms and command autocomplete'
    )
    submit: Call | None = Field(
        default=None,
        title='Executes an action associated with the binding'
    )
    form: Form | None = Field(default=None, title='The modal form to display')
    bindings: list['Binding'] | None = Field(default=None, title='Additional sub-location bindings')


class TopLevelBinding(BaseModel):
    """1 уровень данных о привязках к командам"""
    location: Location = Field(title='Top level location')
    bindings: list[Binding] = Field(title='A list of bindings under this location')


class BindingResponse(BaseModel):
    type: str = 'ok'  # noqa: A003
    data: list[TopLevelBinding]


class User(BaseModel):
    """Пользователь Mattermost"""
    model_config = ConfigDict(from_attributes=True)

    id_: str = Field(alias='id')
    username: str | None = Field(default=None)
    email: EmailStr | None = Field(default=None)

    # noinspection PyNestedDecorators
    @model_validator(mode='before')
    @classmethod
    def parse_email(cls, data: dict):
        if data.get('email') == '':
            data['email'] = None
        if data.get('username') == '':
            data['username'] = None
        return data


class Channel(BaseModel):
    """Канал Mattermost (для передачи данных в ORM)"""
    iid: str = Field(title='Внутренний ID канала', alias='id')
    name: str = Field(title='Название')
    display_name: str | None = Field(title='Видимое название')


class CommandRequestContext(BaseModel):
    bot_user_id: str = Field(serialization_alias='iid')
    bot_access_token: str = Field(serialization_alias='access_token')
    acting_user: User | None = Field(default=None)
    channel: Channel | None = Field(default=None)


class CommandRequest(BaseModel):
    """Структура данных, приходящих с Mattermost, при отправлении команды приложению"""
    path: str
    expand: Expand | None = Field(default=None)
    raw_command: str | None = Field(default=None)
    context: CommandRequestContext | None = Field(default=None)
    values: dict | None = Field(default=None)


class DynamicFieldChoice(BaseModel):
    """Вариант ответа для динамического селект поля"""
    label: str = Field(title='User-facing string')
    value: str = Field(title='Machine-facing value')
    icon_data: str | None = Field(default=None, title='A fully-qualified URL')
