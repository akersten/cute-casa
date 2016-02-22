import persistent, transaction, datetime

class ShoppingListItem(persistent.Persistent):
    """
    A shopping list item is either checked or unchecked, and might TODO in the future keep track of who set it, when it
    was set, etc.
    """
    def __init__(self, title):
        self._title = title
        self._checked = False

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        transaction.commit()

    @property
    def checked(self):
        return self._checked

    @checked.setter
    def checked(self, value):
        self._checked = value
        transaction.commit()

    def toggle(self):
        self.checked = not self.checked

class ShoppingList(persistent.Persistent):
    """
    A shopping list is a collection of things that need to be bought. Shopping lists have a title.
    """

    def __init__(self, title):
        self._title = title
        self._items = []
        transaction.commit()

    def getItems(self):
        return enumerate(self._items)

    def addItem(self, item):
        self._items.append(ShoppingListItem(item))
        self._p_changed = True
        transaction.commit()

    def removeItem(self, itemIdx):
        # TODO: Check itemIdx
        del self._items[itemIdx]
        self._p_changed = True
        transaction.commit()

    def toggleItem(self, itemIdx):
        # TODO: Check itemIdx
        self._items[itemIdx].toggle()