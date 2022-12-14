from __future__ import annotations

from abc import abstractmethod, ABC
from typing import Optional, Any, Generator

from tumfl.Token import Token
from tumfl.utils import generic_str


class ASTNode(ABC):
    def __init__(self, token: Token, name: str) -> None:
        self.name: str = name
        self.token: Token = token
        self.parent_class: Optional[ASTNode] = None

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return all(
            self.__getattribute__(i) == other.__getattribute__(i) for i in self.__dir()
        )

    def __repr__(self) -> str:
        return generic_str(self, ["replace", "parent", "parent_class"])

    def __dir(self) -> Generator[str, None, None]:
        return (
            i
            for i in self.__dir__()
            if not i.startswith("__")
            # ignore "token" for comparison (and parent check)
            and i not in ["replace", "parent", "parent_class", "var", "token"]
        )

    def parent(self, parent: ASTNode) -> None:
        self.parent_class = parent
        for i in self.__dir():
            node: Any = self.__getattribute__(i)
            if isinstance(node, ASTNode):
                node.parent(self)

    @staticmethod
    @abstractmethod
    def from_token(token: Token) -> ASTNode:
        raise NotImplementedError()
