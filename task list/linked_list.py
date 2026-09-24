"""
=====================================================================================
 WORKSHOP: SINGLY LINKED LISTS APPLIED TO A CASE STUDY
 Case study: To-Do List (Task Manager)
 Course: Data Structures

 Description:
     Implementation of a SINGLY LINKED LIST using Object-Oriented Programming,
     where each node represents a TASK and holds a reference (pointer) to the
     next node in the list.

     Node structure:
         [ Task Data | *next ] --> [ Task Data | *next ] --> ... --> None

 This module has NO external dependencies: it can be used standalone (from the
 console) or be consumed by the Flask backend (app.py), which exposes a REST
 API for the web Frontend.
=====================================================================================
"""

from __future__ import annotations
from datetime import datetime
from typing import Optional, List, Dict, Any, Iterator


# --------------------------------------------------------------------------------
# CUSTOM EXCEPTIONS
# --------------------------------------------------------------------------------
class EmptyListError(Exception):
    """Raised when an operation is attempted on an empty linked list."""
    pass


class TaskNotFoundError(Exception):
    """Raised when no task with the requested id is found."""
    pass


class InvalidPriorityError(Exception):
    """Raised when the given priority is not one of the allowed values."""
    pass


VALID_PRIORITIES = ("high", "medium", "low")


# --------------------------------------------------------------------------------
# NODE: basic unit of the linked list
# --------------------------------------------------------------------------------
class Node:
    """
    Represents a node of the singly linked list.

    Each node stores:
        - The data of a task (id, title, description, priority, status)
        - A 'next' pointer that references the following node (or None if it is the last one)
    """

    __slots__ = (
        "id", "title", "description", "priority",
        "completed", "creation_date", "completion_date", "next"
    )

    def __init__(self, id_: int, title: str, description: str = "",
                 priority: str = "medium") -> None:
        self.id: int = id_
        self.title: str = title
        self.description: str = description
        self.priority: str = priority
        self.completed: bool = False
        self.creation_date: datetime = datetime.now()
        self.completion_date: Optional[datetime] = None
        self.next: Optional["Node"] = None  # <-- pointer to the next node

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the node to a dictionary (useful to expose it as JSON in the API)."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "completed": self.completed,
            "creation_date": self.creation_date.strftime("%Y-%m-%d %H:%M:%S"),
            "completion_date": (
                self.completion_date.strftime("%Y-%m-%d %H:%M:%S")
                if self.completion_date else None
            ),
        }

    def __repr__(self) -> str:
        status = "done" if self.completed else "pending"
        return f"Node(id={self.id}, title='{self.title}', status={status})"


# --------------------------------------------------------------------------------
# SINGLY LINKED LIST: main structure (container class)
# --------------------------------------------------------------------------------
class TaskList:
    """
    Singly Linked List that manages Task nodes.

    Keeps references to:
        - self.head  -> first node of the list
        - self.tail  -> last node of the list, enables O(1) insertion at the end
        - self.size  -> current number of nodes

    Time complexity of the main operations:
        add_task (append)             -> O(1)   (thanks to the 'tail' pointer)
        add_to_start                  -> O(1)
        find_task / update_task       -> O(n)
        remove_task                   -> O(n)
        traverse / list all           -> O(n)
    """

    def __init__(self) -> None:
        self.head: Optional[Node] = None
        self.tail: Optional[Node] = None
        self.size: int = 0
        self._id_counter: int = 1  # auto-increment, simulates a PK

    # ------------------------------------------------------------------
    # Basic utilities
    # ------------------------------------------------------------------
    def is_empty(self) -> bool:
        return self.head is None

    def __len__(self) -> int:
        return self.size

    def __iter__(self) -> Iterator[Node]:
        """Allows traversing the list with a 'for node in task_list:'."""
        current = self.head
        while current is not None:
            yield current
            current = current.next

    def __repr__(self) -> str:
        return f"TaskList(size={self.size})"

    # ------------------------------------------------------------------
    # INSERTION
    # ------------------------------------------------------------------
    def add_task(self, title: str, description: str = "",
                 priority: str = "medium") -> Node:
        """
        Inserts a new node at the END of the linked list. O(1)

        1. A node is created holding the task data.
        2. If the list is empty, the new node becomes both head and tail.
        3. Otherwise, the current 'tail' node points (next) to the new node,
           and the new node becomes the new tail.
        """
        title = (title or "").strip()
        if not title:
            raise ValueError("The task title cannot be empty.")
        priority = (priority or "medium").lower().strip()
        if priority not in VALID_PRIORITIES:
            raise InvalidPriorityError(
                f"Invalid priority '{priority}'. Use: {VALID_PRIORITIES}"
            )

        new_node = Node(self._id_counter, title, description, priority)
        self._id_counter += 1

        if self.is_empty():
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node   # the last node points to the new one
            self.tail = new_node        # the new node is now the last one

        self.size += 1
        return new_node

    def add_to_start(self, title: str, description: str = "",
                      priority: str = "medium") -> Node:
        """Inserts a new node at the START of the list. O(1)"""
        title = (title or "").strip()
        if not title:
            raise ValueError("The task title cannot be empty.")
        priority = (priority or "medium").lower().strip()
        if priority not in VALID_PRIORITIES:
            raise InvalidPriorityError(f"Invalid priority '{priority}'.")

        new_node = Node(self._id_counter, title, description, priority)
        self._id_counter += 1

        new_node.next = self.head
        self.head = new_node
        if self.tail is None:  # list was empty
            self.tail = new_node

        self.size += 1
        return new_node

    # ------------------------------------------------------------------
    # SEARCH
    # ------------------------------------------------------------------
    def find_task(self, id_: int) -> Node:
        """Traverses the list node by node until the requested id is found. O(n)"""
        current = self.head
        while current is not None:
            if current.id == id_:
                return current
            current = current.next
        raise TaskNotFoundError(f"No task found with id={id_}.")

    def exists(self, id_: int) -> bool:
        try:
            self.find_task(id_)
            return True
        except TaskNotFoundError:
            return False

    # ------------------------------------------------------------------
    # DELETION
    # ------------------------------------------------------------------
    def remove_task(self, id_: int) -> bool:
        """
        Removes the node whose id matches, re-linking the previous node
        directly to the node following the removed one. O(n)
        """
        if self.is_empty():
            raise EmptyListError("Cannot remove: the list is empty.")

        previous: Optional[Node] = None
        current = self.head

        while current is not None:
            if current.id == id_:
                if previous is None:
                    # Removing the head
                    self.head = current.next
                else:
                    # "Skip" the removed node by linking previous -> next
                    previous.next = current.next

                if current is self.tail:
                    self.tail = previous  # update tail if the last node was removed

                self.size -= 1
                return True

            previous = current
            current = current.next

        raise TaskNotFoundError(f"No task found with id={id_}.")

    def clear(self) -> None:
        """Removes all nodes from the list. O(1) (references are simply discarded)."""
        self.head = None
        self.tail = None
        self.size = 0

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------
    def update_task(self, id_: int, title: Optional[str] = None,
                     description: Optional[str] = None,
                     priority: Optional[str] = None) -> Node:
        """Modifies the data of the found node, without altering the pointers."""
        node = self.find_task(id_)
        if title is not None:
            title = title.strip()
            if not title:
                raise ValueError("The title cannot be left empty.")
            node.title = title
        if description is not None:
            node.description = description
        if priority is not None:
            priority = priority.lower().strip()
            if priority not in VALID_PRIORITIES:
                raise InvalidPriorityError(f"Invalid priority '{priority}'.")
            node.priority = priority
        return node

    def mark_completed(self, id_: int, completed: bool = True) -> Node:
        """Changes the completion status of a task (toggle or explicit)."""
        node = self.find_task(id_)
        node.completed = completed
        node.completion_date = datetime.now() if completed else None
        return node

    def toggle_completed(self, id_: int) -> Node:
        node = self.find_task(id_)
        return self.mark_completed(id_, not node.completed)

    # ------------------------------------------------------------------
    # REORDERING (extra operation typical of linked lists)
    # ------------------------------------------------------------------
    def move_to_start(self, id_: int) -> None:
        """Unlinks an existing node and re-links it as the new head. O(n)"""
        if self.head is None or self.head.id == id_:
            return
        previous = self.head
        current = self.head.next
        while current is not None:
            if current.id == id_:
                previous.next = current.next
                if current is self.tail:
                    self.tail = previous
                current.next = self.head
                self.head = current
                return
            previous = current
            current = current.next
        raise TaskNotFoundError(f"No task found with id={id_}.")

    def reverse(self) -> None:
        """
        Reverses the linked list in place, redirecting each node's 'next'
        pointer in the opposite direction. A classic singly linked list
        exercise. O(n) time, O(1) extra space.
        """
        previous: Optional[Node] = None
        current = self.head
        self.tail = self.head
        while current is not None:
            temp_next = current.next
            current.next = previous
            previous = current
            current = temp_next
        self.head = previous

    # ------------------------------------------------------------------
    # QUERIES / REPORTS
    # ------------------------------------------------------------------
    def get_all(self) -> List[Dict[str, Any]]:
        return [node.to_dict() for node in self]

    def get_pending(self) -> List[Dict[str, Any]]:
        return [n.to_dict() for n in self if not n.completed]

    def get_completed(self) -> List[Dict[str, Any]]:
        return [n.to_dict() for n in self if n.completed]

    def filter_by_priority(self, priority: str) -> List[Dict[str, Any]]:
        priority = priority.lower().strip()
        return [n.to_dict() for n in self if n.priority == priority]

    def get_statistics(self) -> Dict[str, Any]:
        total = self.size
        completed = sum(1 for n in self if n.completed)
        pending = total - completed
        by_priority = {p: 0 for p in VALID_PRIORITIES}
        for n in self:
            by_priority[n.priority] += 1
        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "completion_percentage": round((completed / total * 100), 1) if total else 0.0,
            "by_priority": by_priority,
        }

    def print_list(self) -> None:
        """Traverses and prints the list to the console (classic textbook traversal)."""
        if self.is_empty():
            print("The task list is empty.")
            return
        current = self.head
        print("=" * 60)
        while current is not None:
            status = "Completed" if current.completed else "Pending"
            print(f"[{current.id}] {current.title}  |  Priority: {current.priority}  |  {status}")
            print(f"     Description: {current.description or '(no description)'}")
            print(f"     Next -> {current.next.id if current.next else 'None'}")
            print("-" * 60)
            current = current.next


# --------------------------------------------------------------------------------
# CONSOLE DEMO (run: python linked_list.py)
# --------------------------------------------------------------------------------
if __name__ == "__main__":
    task_list = TaskList()

    task_list.add_task("Study linked lists", "Review the theory of nodes and pointers", "high")
    task_list.add_task("Do the Python workshop", "Implement the TaskList class", "high")
    task_list.add_task("Build the Frontend", "Connect HTML/JS with the Flask API", "medium")
    task_list.add_task("Review for the midterm", "", "low")

    print("\n>>> Full task list:")
    task_list.print_list()

    print("\n>>> Marking task id=1 as completed")
    task_list.mark_completed(1)

    print("\n>>> Removing task id=3")
    task_list.remove_task(3)

    print("\n>>> List after the modifications:")
    task_list.print_list()

    print("\n>>> Statistics:")
    print(task_list.get_statistics())
