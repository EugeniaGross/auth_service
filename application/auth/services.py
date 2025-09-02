from auth.exceptions import UserNotFoundError, VerifyPasswordError
from auth.repositories import UsersAbstractRepository
from auth.schemes import UserRequestScheme
from utils.hashes import HashService


class UserService:
    """
    Сервис для работы с пользователями.
    Инкапсулирует бизнес-логику, связанную с пользователями:
    - добавление нового пользователя с хэшированием пароля;
    - поиск пользователя по email;
    - аутентификация пользователя.

    Внешние зависимости: UsersAbstractRepository, HashService.
    """

    def __init__(
        self, repo: UsersAbstractRepository, hash_service: HashService
    ):
        """
        Инициализация сервиса пользователей.
        Args:
            repo (UsersAbstractRepository): Репозиторий для работы с БД.
            hash_service (HashService): Сервис для хэширования и проверки паролей.
        """
        self.repo: UsersAbstractRepository = repo
        self.hash_service: HashService = hash_service

    async def add_one(self, user: UserRequestScheme):
        """
        Добавляет нового пользователя.
        - Пароль пользователя хэшируется.
        - Оригинальный пароль удаляется перед сохранением.
        - Пользователь сохраняется в БД.
        Args:
            user (UserRequestScheme): Данные пользователя.
        Returns:
            User: Пользователь.
        """
        user = user.model_dump()
        hash_password = self.hash_service.create_hash_password(
            user["password"]
        )
        user["hash_password"] = hash_password
        del user["password"]
        user = await self.repo.add_one(user)
        return user

    async def get_one_by_email(self, email: str):
        """
        Получает пользователя по email.
        Args:
            email (str): Электронная почта пользователя.
        Returns:
            Optional[User]: Пользователь или None.
        """
        return await self.repo.get_one_by_email(email)

    async def authenticate_user(self, auth_user: UserRequestScheme):
        """
        Аутентифицирует пользователя по email и паролю.
        - Проверяет, существует ли пользователь.
        - Сравнивает хэшированный пароль с введённым.
        - В случае ошибок выбрасывает исключения.
        Args:
            auth_user (UserRequestScheme): Данные для входа (email и пароль).
        Returns:
            User: Пользователь.
        Raises:
            UserNotFoundError: Если пользователь с указанным email не найден.
            VerifyPasswordError: Если пароль введён неверно.
        """
        user = await self.get_one_by_email(auth_user.email)
        if user is None:
            raise UserNotFoundError("Пользователь не найден")
        if not self.hash_service.verify_password(
            auth_user.password, user.hash_password
        ):
            raise VerifyPasswordError("Пароль введен не верно")
        return user

    async def get_one(self, id: int):
        """
        Получает пользователя по id.
        Args:
            id (str): Идентификатор пользователя.
        Returns:
            Optional[User]: Пользователь или None.
        """
        return await self.repo.get_one(id)
