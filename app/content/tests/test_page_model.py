import pytest

from app.content.factories.page_factory import PageFactory, ParentPageFactory


@pytest.mark.django_db
def test_pages_do_not_reorder_with_initial_correct_order():
    """Test that pages don't switch position when order starts correct"""

    parent_page = ParentPageFactory()

    page_created_first = PageFactory(parent=parent_page, order=0)
    page_created_second = PageFactory(parent=parent_page, order=1)

    first_child = parent_page.children.all()[0]
    second_child = parent_page.children.all()[1]

    assert page_created_first == first_child
    assert page_created_second == second_child


@pytest.mark.django_db
def test_pages_reorder_with_initial_wrong_order():
    """Test that updating pages work, by creating pages in wrong order"""

    parent_page = ParentPageFactory()

    page_created_first = PageFactory(parent=parent_page, order=1)
    page_created_second = PageFactory(parent=parent_page, order=0)

    first_child = parent_page.children.all()[0]
    second_child = parent_page.children.all()[1]

    assert not page_created_first == first_child
    assert not page_created_second == second_child
