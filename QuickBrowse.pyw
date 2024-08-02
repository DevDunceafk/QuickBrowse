import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QAction, QLineEdit, QComboBox, 
    QTabWidget, QStatusBar, QMenuBar, QMenu, QMessageBox, QDialog, QVBoxLayout, QLabel
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtGui import QIcon

class QuickBrowse(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QuickBrowse")
        self.setGeometry(300, 150, 1200, 800)

        self.history = []

        # Set up the tab widget
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)

        self.setCentralWidget(self.tabs)

        # Create a status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)

        # Create the navigation bar
        navtb = QToolBar("Navigation")
        self.addToolBar(navtb)

        # Back button
        back_btn = QAction(QIcon.fromTheme("go-previous"), "Back", self)
        back_btn.triggered.connect(self.navigate_back)
        navtb.addAction(back_btn)

        # Forward button
        forward_btn = QAction(QIcon.fromTheme("go-next"), "Forward", self)
        forward_btn.triggered.connect(self.navigate_forward)
        navtb.addAction(forward_btn)

        # Reload button
        reload_btn = QAction(QIcon.fromTheme("view-refresh"), "Reload", self)
        reload_btn.triggered.connect(self.reload_page)
        navtb.addAction(reload_btn)

        # Stop button
        stop_btn = QAction(QIcon.fromTheme("process-stop"), "Stop", self)
        stop_btn.triggered.connect(self.stop_loading)
        navtb.addAction(stop_btn)

        # Home button
        home_btn = QAction(QIcon.fromTheme("go-home"), "Home", self)
        home_btn.triggered.connect(self.navigate_home)
        navtb.addAction(home_btn)

        # URL bar
        self.urlbar = QLineEdit()
        self.urlbar.setPlaceholderText("Enter URL or search query")
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        navtb.addWidget(self.urlbar)

        # Search engine selection
        self.search_engine_selector = QComboBox()
        self.search_engine_selector.addItems(["Google", "Brave", "Bing", "DuckDuckGo", "Startpage"])
        self.search_engine_selector.currentIndexChanged.connect(self.navigate_home)
        navtb.addWidget(self.search_engine_selector)

        # Search button
        search_btn = QAction(QIcon.fromTheme("edit-find"), "Search", self)
        search_btn.triggered.connect(self.navigate_to_url)
        navtb.addAction(search_btn)

        # Create menu bar
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)

        # File menu
        file_menu = QMenu("File", self)
        menubar.addMenu(file_menu)

        # New tab action
        new_tab_action = QAction(QIcon.fromTheme("tab-new"), "New Tab", self)
        new_tab_action.setShortcut("Ctrl+T")
        new_tab_action.triggered.connect(self.add_new_tab)
        file_menu.addAction(new_tab_action)

        # Close tab action
        close_tab_action = QAction(QIcon.fromTheme("tab-close"), "Close Tab", self)
        close_tab_action.setShortcut("Ctrl+W")
        close_tab_action.triggered.connect(self.close_current_tab)
        file_menu.addAction(close_tab_action)

        # History menu
        history_menu = QMenu("History", self)
        menubar.addMenu(history_menu)

        # Show history action
        show_history_action = QAction(QIcon.fromTheme("document-open-recent"), "Show History", self)
        show_history_action.triggered.connect(self.show_history)
        history_menu.addAction(show_history_action)

        # Bookmarks menu
        bookmarks_menu = QMenu("Bookmarks", self)
        menubar.addMenu(bookmarks_menu)

        # Add bookmark action
        add_bookmark_action = QAction(QIcon.fromTheme("bookmark-new"), "Add Bookmark", self)
        add_bookmark_action.triggered.connect(self.add_bookmark)
        bookmarks_menu.addAction(add_bookmark_action)

        # Bookmark list
        self.bookmarks_menu = bookmarks_menu

        # Initialize the browser with one tab
        self.add_new_tab(QUrl("https://www.google.com"), "Homepage")

        # Apply custom styles
        self.apply_styles()

        self.show()

    def apply_styles(self):
        style_sheet = """
        QMainWindow {
            background-color: #f0f0f0;
        }
        QToolBar {
            background-color: #4d4d4d;
            spacing: 10px;
            padding: 5px;
        }
        QToolButton {
            background-color: #4d4d4d;
            border: none;
            color: white;
        }
        QToolButton:hover {
            background-color: #555555;
        }
        QLineEdit {
            background-color: white;
            border: 1px solid #c4c4c4;
            padding: 5px;
            border-radius: 10px;
            margin-right: 10px;
            font-size: 16px;
        }
        QComboBox {
            background-color: white;
            border: 1px solid #c4c4c4;
            padding: 5px;
            border-radius: 10px;
            font-size: 16px;
        }
        QMenuBar {
            background-color: #333333;
            color: white;
            font-size: 16px;
        }
        QMenuBar::item {
            background-color: #333333;
            padding: 5px 10px;
        }
        QMenuBar::item:selected {
            background-color: #444444;
        }
        QMenu {
            background-color: #4d4d4d;
            color: white;
        }
        QMenu::item {
            padding: 5px 10px;
        }
        QMenu::item:selected {
            background-color: #555555;
        }
        """
        self.setStyleSheet(style_sheet)

    def add_new_tab(self, qurl=None, label="Blank"):
        if qurl is None or not isinstance(qurl, QUrl):
            qurl = QUrl(self.current_search_engine_homepage())

        browser = QWebEngineView()
        # Adjust QWebEngineSettings for smoother scrolling
        settings = browser.settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.ScrollAnimatorEnabled, True)

        browser.setUrl(qurl)
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)

        browser.urlChanged.connect(lambda qurl, browser=browser: self.update_urlbar(qurl, browser))
        browser.urlChanged.connect(lambda qurl, browser=browser: self.add_to_history(qurl, browser))
        browser.loadFinished.connect(lambda _, i=i, browser=browser: self.tabs.setTabText(i, browser.page().title()))
        browser.loadStarted.connect(lambda: self.status.showMessage("Loading..."))
        browser.loadFinished.connect(lambda: self.status.showMessage(""))

    def tab_open_doubleclick(self, i):
        if i == -1:  # No tab under the click
            self.add_new_tab()

    def current_tab_changed(self, i):
        qurl = self.tabs.currentWidget().url()
        self.update_urlbar(qurl, self.tabs.currentWidget())
        self.update_title(self.tabs.currentWidget())

    def close_current_tab(self, i=None):
        if self.tabs.count() < 2:
            return

        if i is None:
            i = self.tabs.currentIndex()

        self.tabs.removeTab(i)

    def update_title(self, browser):
        if browser != self.tabs.currentWidget():
            return

        title = self.tabs.currentWidget().page().title()
        self.setWindowTitle(f"{title} - QuickBrowse")

    def navigate_home(self):
        self.tabs.currentWidget().setUrl(QUrl(self.current_search_engine_homepage()))

    def navigate_to_url(self):
        url = self.urlbar.text()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = f"https://{self.current_search_engine()}/search?q=" + url
        self.tabs.currentWidget().setUrl(QUrl(url))

    def update_urlbar(self, q, browser=None):
        if browser != self.tabs.currentWidget():
            return

        self.urlbar.setText(q.toString())
        self.urlbar.setCursorPosition(0)

    def current_search_engine(self):
        engine = self.search_engine_selector.currentText()
        if engine == "Google":
            return "www.google.com"
        elif engine == "Brave":
            return "search.brave.com"
        elif engine == "Bing":
            return "www.bing.com"
        elif engine == "DuckDuckGo":
            return "duckduckgo.com"
        elif engine == "Startpage":
            return "www.startpage.com"

    def current_search_engine_homepage(self):
        engine = self.search_engine_selector.currentText()
        if engine == "Google":
            return "https://www.google.com"
        elif engine == "Brave":
            return "https://search.brave.com"
        elif engine == "Bing":
            return "https://www.bing.com"
        elif engine == "DuckDuckGo":
            return "https://www.duckduckgo.com"
        elif engine == "Startpage":
            return "https://www.startpage.com"

    def add_to_history(self, qurl, browser):
        if browser == self.tabs.currentWidget():
            self.history.append(qurl.toString())

    def show_history(self):
        history_dialog = QDialog(self)
        history_dialog.setWindowTitle("Browsing History")
        layout = QVBoxLayout()
        for url in self.history:
            label = QLabel(url)
            layout.addWidget(label)
        history_dialog.setLayout(layout)
        history_dialog.exec_()

    def add_bookmark(self):
        url = self.tabs.currentWidget().url().toString()
        title = self.tabs.currentWidget().page().title()
        bookmark_action = QAction(title, self)
        bookmark_action.triggered.connect(lambda: self.tabs.currentWidget().setUrl(QUrl(url)))
        self.bookmarks_menu.addAction(bookmark_action)
        QMessageBox.information(self, "Bookmark Added", f"Added bookmark: {title}")

    def navigate_back(self):
        self.tabs.currentWidget().back()

    def navigate_forward(self):
        self.tabs.currentWidget().forward()

    def reload_page(self):
        self.tabs.currentWidget().reload()

    def stop_loading(self):
        self.tabs.currentWidget().stop()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    QApplication.setApplicationName("QuickBrowse")
    window = QuickBrowse()
    sys.exit(app.exec_())
