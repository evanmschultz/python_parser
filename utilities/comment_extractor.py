from libcst import CSTNode, EmptyLine, Comment

from models.models import CommentModel
from models.enums import CommentType


class CommentExtractor:
    @staticmethod
    def get_important_comment(
        comment_or_empty_line_node: CSTNode,
    ) -> CommentModel | None:
        if (
            isinstance(comment_or_empty_line_node, EmptyLine)
            and comment_or_empty_line_node.comment
        ):
            comment_text: str | None = comment_or_empty_line_node.comment.value
        elif isinstance(comment_or_empty_line_node, Comment):
            comment_text: str | None = comment_or_empty_line_node.value
        else:
            return None

        comment_type: CommentType | None = next(
            (ct for ct in CommentType if ct.value in comment_text), None
        )
        if comment_type:
            return CommentModel(
                content=comment_text,
                comment_type=comment_type,
            )
