import tkinter as tk
from tkinter import filedialog, messagebox
import os
import unittest

class DocumentParser:
    """Parses text documents."""
    def parse_document(self, filepath):
        try:
            with open(filepath, 'r') as f:
                text = f.read().lower()
                words = text.split()
                return words
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: File not found at {filepath}")
        except Exception as e:
            raise Exception(f"An error occurred while reading {filepath}: {e}")

class IndexBuilder:
    """Builds an inverted index from a directory of text files."""
    def __init__(self, parser=None):
        self.parser = parser or DocumentParser()

    def build_index(self, directory):
        if not os.path.isdir(directory):
            raise NotADirectoryError(f"Error: '{directory}' is not a valid directory.")

        local_index = {}
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if filepath.endswith(".txt"):
                try:
                    words = self.parser.parse_document(filepath)
                    for word in words:
                        if word in local_index:
                            if filepath not in local_index[word]:
                                local_index[word].append(filepath)
                        else:
                            local_index[word] = [filepath]
                except (FileNotFoundError, Exception) as e:
                    messagebox.showerror("Indexing Error", str(e))
        return local_index

class SearchEngine:
    """Searches the document index."""
    def __init__(self, index=None, sorter=None):
        self.index = index if index is not None else {}
        self.sorter = sorter or self._merge_sort

    def _merge(self, left, right):
        merged = []
        left_index = 0
        right_index = 0

        while left_index < len(left) and right_index < len(right):
            if left[left_index] < right[right_index]:
                merged.append(left[left_index])
                left_index += 1
            else:
                merged.append(right[right_index])
                right_index += 1

        merged.extend(left[left_index:])
        merged.extend(right[right_index:])
        return merged

    def _merge_sort(self, data):
        if len(data) <= 1:
            return data
        mid = len(data) // 2
        left = data[:mid]
        right = data[mid:]
        left_sorted = self._merge_sort(left)
        right_sorted = self._merge_sort(right)
        return self._merge(left_sorted, right_sorted)

    def search_index(self, search_term):
        if not search_term:
            return []
        search_term_lower = search_term.lower()
        if search_term_lower in self.index:
            results = self.index[search_term_lower]
            sorted_results = self._merge_sort(list(set(results))) # Ensure unique and sorted results
            return sorted_results
        else:
            return []

class DocumentSearchApp:
    """GUI application for searching documents."""
    def __init__(self, master):
        self.master = master
        master.title("Document Search Application")

        self.parser = DocumentParser()
        self.index_builder = IndexBuilder(self.parser)
        self.search_engine = SearchEngine()
        self.document_index = {}
        self.document_directory_var = tk.StringVar()

        self._create_widgets()

    def _create_widgets(self):
        # Directory Selection
        tk.Label(self.master, text="Select Document Directory:").pack(pady=5)
        tk.Entry(self.master, textvariable=self.document_directory_var, width=50).pack(pady=5)
        tk.Button(self.master, text="Browse", command=self._browse_directory).pack(pady=5)

        # Indexing
        tk.Button(self.master, text="Index Documents", command=self._index_documents).pack(pady=10)

        # Search
        tk.Label(self.master, text="Enter Search Term:").pack(pady=5)
        self.search_entry = tk.Entry(self.master, textvariable=tk.StringVar(), width=50)
        self.search_entry.pack(pady=5)
        tk.Button(self.master, text="Search", command=self._perform_search).pack(pady=5)

        # Results
        self.results_listbox = tk.Listbox(self.master, width=70, height=15)
        self.results_listbox.pack(pady=10)

    def _browse_directory(self):
        directory = filedialog.askdirectory()
        self.document_directory_var.set(directory)

    def _index_documents(self):
        directory = self.document_directory_var.get()
        if not directory:
            messagebox.showerror("Error", "Please select a document directory first.")
            return

        try:
            self.document_index = self.index_builder.build_index(directory)
            self.search_engine.index = self.document_index
            messagebox.showinfo("Indexing Complete", f"Successfully indexed documents in:\n{directory}")
        except (NotADirectoryError, Exception) as e:
            messagebox.showerror("Indexing Error", str(e))

    def _perform_search(self):
        search_term = self.search_entry.get()
        if not self.document_index:
            messagebox.showerror("Error", "Please index the documents first.")
            return

        if not search_term.strip():
            messagebox.showinfo("Search Info", "Please enter a search term.")
            self.results_listbox.delete(0, tk.END)
            return

        results = self.search_engine.search_index(search_term)
        self.results_listbox.delete(0, tk.END) # Clear previous results
        if results:
            for filepath in results:
                self.results_listbox.insert(tk.END, filepath)
        else:
            self.results_listbox.insert(tk.END, "No results found.")

class TestDocumentSearch(unittest.TestCase):
    def setUp(self):
        # Create dummy files and directory for testing
        self.test_dir = "test_documents"
        os.makedirs(self.test_dir, exist_ok=True)
        with open(os.path.join(self.test_dir, "file1.txt"), "w") as f:
            f.write("This is a test document with the word test.")
        with open(os.path.join(self.test_dir, "file2.txt"), "w") as f:
            f.write("Another document containing the word another.")
        with open(os.path.join(self.test_dir, "file3.txt"), "w") as f:
            f.write("This file has the word test again.")

        self.parser = DocumentParser()
        self.index_builder = IndexBuilder(self.parser)
        self.search_engine = SearchEngine()

    def tearDown(self):
        # Clean up dummy files and directory
        import shutil
        shutil.rmtree(self.test_dir)

    def test_parse_document(self):
        filepath = os.path.join(self.test_dir, "file1.txt")
        words = self.parser.parse_document(filepath)
        self.assertEqual(words, ["this", "is", "a", "test", "document", "with", "the", "word", "test."])

    def test_build_index(self):
        index = self.index_builder.build_index(self.test_dir)
        self.assertIn("test", index)
        self.assertEqual(len(index["test"]), 2)
        self.assertIn(os.path.join(self.test_dir, "file1.txt"), index["test"])
        self.assertIn(os.path.join(self.test_dir, "file3.txt"), index["test"])
        self.assertIn("another", index)
        self.assertEqual(len(index["another"]), 1)
        self.assertIn(os.path.join(self.test_dir, "file2.txt"), index["another"])

    def test_search_index_found(self):
        index = self.index_builder.build_index(self.test_dir)
        self.search_engine.index = index
        results = self.search_engine.search_index("test")
        self.assertEqual(len(results), 2)
        self.assertIn(os.path.join(self.test_dir, "file1.txt"), results)
        self.assertIn(os.path.join(self.test_dir, "file3.txt"), results)

    def test_search_index_not_found(self):
        index = self.index_builder.build_index(self.test_dir)
        self.search_engine.index = index
        results = self.search_engine.search_index("nonexistentword")
        self.assertEqual(len(results), 0)

    def test_search_index_empty_term(self):
        index = self.index_builder.build_index(self.test_dir)
        self.search_engine.index = index
        results = self.search_engine.search_index("")
        self.assertEqual(len(results), 0)

if __name__ == "__main__":
    root = tk.Tk()
    app = DocumentSearchApp(root)
    root.mainloop()

    # Run unit tests if the script is executed directly
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDocumentSearch))
    runner = unittest.TextTestRunner()
    print("\nRunning Unit Tests:")
    runner.run(suite)
