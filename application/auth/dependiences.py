from auth.repositories import UsersPostgreSQLRepository
from auth.services import UserService
from utils.hashes import HashService


def user_service():
    return UserService(UsersPostgreSQLRepository, HashService)
