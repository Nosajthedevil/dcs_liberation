import logging
import textwrap
from typing import Callable

from PySide2.QtCore import QItemSelectionModel, QPoint, QSize, Qt
from PySide2.QtGui import QStandardItem, QStandardItemModel
from PySide2.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDialog,
    QGridLayout,
    QGroupBox,
    QLabel,
    QListView,
    QPushButton,
    QSpinBox,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)

import qt_ui.uiconstants as CONST
from game.game import Game
from game.settings import (
    BooleanOption,
    BoundedFloatOption,
    BoundedIntOption,
    ChoicesOption,
    OptionDescription,
    Settings,
)
from qt_ui.widgets.QLabeledWidget import QLabeledWidget
from qt_ui.widgets.spinsliders import FloatSpinSlider, TimeInputs
from qt_ui.windows.GameUpdateSignal import GameUpdateSignal
from qt_ui.windows.finances.QFinancesMenu import QHorizontalSeparationLine
from qt_ui.windows.settings.plugins import PluginOptionsPage, PluginsPage


class CheatSettingsBox(QGroupBox):
    def __init__(self, game: Game, apply_settings: Callable[[], None]) -> None:
        super().__init__("Cheat Settings")
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.red_ato_checkbox = QCheckBox()
        self.red_ato_checkbox.setChecked(game.settings.show_red_ato)
        self.red_ato_checkbox.toggled.connect(apply_settings)

        self.frontline_cheat_checkbox = QCheckBox()
        self.frontline_cheat_checkbox.setChecked(game.settings.enable_frontline_cheats)
        self.frontline_cheat_checkbox.toggled.connect(apply_settings)

        self.base_capture_cheat_checkbox = QCheckBox()
        self.base_capture_cheat_checkbox.setChecked(
            game.settings.enable_base_capture_cheat
        )
        self.base_capture_cheat_checkbox.toggled.connect(apply_settings)

        self.red_ato = QLabeledWidget("Show Red ATO:", self.red_ato_checkbox)
        self.main_layout.addLayout(self.red_ato)
        self.frontline_cheat = QLabeledWidget(
            "Enable Frontline Cheats:", self.frontline_cheat_checkbox
        )
        self.main_layout.addLayout(self.frontline_cheat)
        self.base_capture_cheat = QLabeledWidget(
            "Enable Base Capture Cheat:", self.base_capture_cheat_checkbox
        )
        self.main_layout.addLayout(self.base_capture_cheat)

    @property
    def show_red_ato(self) -> bool:
        return self.red_ato_checkbox.isChecked()

    @property
    def show_frontline_cheat(self) -> bool:
        return self.frontline_cheat_checkbox.isChecked()

    @property
    def show_base_capture_cheat(self) -> bool:
        return self.base_capture_cheat_checkbox.isChecked()


class PilotSettingsBox(QGroupBox):
    def __init__(self, game: Game) -> None:
        super().__init__("Pilots and Squadrons")
        self.game = game

        layout = QGridLayout()
        self.setLayout(layout)

        self.ai_pilot_levelling = QCheckBox()
        self.ai_pilot_levelling.setChecked(self.game.settings.ai_pilot_levelling)
        self.ai_pilot_levelling.toggled.connect(self.set_ai_pilot_leveling)

        ai_pilot_levelling_info = (
            "Set whether or not AI pilots will level up after completing a number of"
            " sorties. Since pilot level affects the AI skill, you may wish to disable"
            " this, lest you face an Ace!"
        )

        self.ai_pilot_levelling.setToolTip(ai_pilot_levelling_info)
        ai_pilot_levelling_label = QLabel("Allow AI pilot levelling")
        ai_pilot_levelling_label.setToolTip(ai_pilot_levelling_info)

        layout.addWidget(ai_pilot_levelling_label, 0, 0)
        layout.addWidget(self.ai_pilot_levelling, 0, 1, Qt.AlignRight)

        enable_squadron_pilot_limits_info = (
            "If set, squadrons will be limited to a maximum number of pilots and dead "
            "pilots will replenish at a fixed rate, each defined with the settings"
            "below. Auto-purchase may buy aircraft for which there are no pilots"
            "available, so this feature is still a work-in-progress."
        )

        enable_squadron_pilot_limits_label = QLabel(
            "Enable per-squadron pilot limits (WIP)"
        )
        enable_squadron_pilot_limits_label.setToolTip(enable_squadron_pilot_limits_info)
        enable_squadron_pilot_limits = QCheckBox()
        enable_squadron_pilot_limits.setToolTip(enable_squadron_pilot_limits_info)
        enable_squadron_pilot_limits.setChecked(
            self.game.settings.enable_squadron_pilot_limits
        )
        enable_squadron_pilot_limits.toggled.connect(
            self.set_enable_squadron_pilot_limits
        )

        layout.addWidget(enable_squadron_pilot_limits_label, 1, 0)
        layout.addWidget(enable_squadron_pilot_limits, 1, 1, Qt.AlignRight)

        self.pilot_limit = QSpinBox()
        self.pilot_limit.setMinimum(12)
        self.pilot_limit.setMaximum(72)
        self.pilot_limit.setValue(self.game.settings.squadron_pilot_limit)
        self.pilot_limit.setEnabled(self.game.settings.enable_squadron_pilot_limits)
        self.pilot_limit.valueChanged.connect(self.set_squadron_pilot_limit)

        pilot_limit_info = (
            "Sets the maximum number of pilots a squadron may have active. "
            "Changing this value will not have an immediate effect, but will alter "
            "replenishment for future turns."
        )

        self.pilot_limit.setToolTip(pilot_limit_info)
        pilot_limit_label = QLabel("Maximum number of pilots per squadron")
        pilot_limit_label.setToolTip(pilot_limit_info)

        layout.addWidget(pilot_limit_label, 2, 0)
        layout.addWidget(self.pilot_limit, 2, 1, Qt.AlignRight)

        self.squadron_replenishment_rate = QSpinBox()
        self.squadron_replenishment_rate.setMinimum(1)
        self.squadron_replenishment_rate.setMaximum(20)
        self.squadron_replenishment_rate.setValue(
            self.game.settings.squadron_replenishment_rate
        )
        self.squadron_replenishment_rate.setEnabled(
            self.game.settings.enable_squadron_pilot_limits
        )
        self.squadron_replenishment_rate.valueChanged.connect(
            self.set_squadron_replenishment_rate
        )

        squadron_replenishment_rate_info = (
            "Sets the maximum number of pilots that will be recruited to each squadron "
            "at the end of each turn. Squadrons will not recruit new pilots beyond the "
            "pilot limit, but each squadron with room for more pilots will recruit "
            "this many pilots each turn up to the limit."
        )

        self.squadron_replenishment_rate.setToolTip(squadron_replenishment_rate_info)
        squadron_replenishment_rate_label = QLabel("Squadron pilot replenishment rate")
        squadron_replenishment_rate_label.setToolTip(squadron_replenishment_rate_info)

        layout.addWidget(squadron_replenishment_rate_label, 3, 0)
        layout.addWidget(self.squadron_replenishment_rate, 3, 1, Qt.AlignRight)

    def set_enable_squadron_pilot_limits(self, checked: bool) -> None:
        self.game.settings.enable_squadron_pilot_limits = checked
        self.pilot_limit.setEnabled(checked)
        self.squadron_replenishment_rate.setEnabled(checked)

    def set_squadron_pilot_limit(self, value: int) -> None:
        self.game.settings.squadron_pilot_limit = value

    def set_squadron_replenishment_rate(self, value: int) -> None:
        self.game.settings.squadron_replenishment_rate = value

    def set_ai_pilot_leveling(self, checked: bool) -> None:
        self.game.settings.ai_pilot_levelling = checked


START_TYPE_TOOLTIP = "Selects the start type used for AI aircraft."


class StartTypeComboBox(QComboBox):
    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self.settings = settings
        self.addItems(["Cold", "Warm", "Runway", "In Flight"])
        self.currentTextChanged.connect(self.on_change)
        self.setToolTip(START_TYPE_TOOLTIP)

    def on_change(self, value: str) -> None:
        self.settings.default_start_type = value


class AutoSettingsLayout(QGridLayout):
    def __init__(self, page: str, section: str, settings: Settings) -> None:
        super().__init__()
        self.settings = settings

        for row, (name, description) in enumerate(Settings.fields(page, section)):
            self.add_label(row, description)
            if isinstance(description, BooleanOption):
                self.add_checkbox_for(row, name, description)
            elif isinstance(description, ChoicesOption):
                self.add_combobox_for(row, name, description)
            elif isinstance(description, BoundedFloatOption):
                self.add_float_spin_slider_for(row, name, description)
            elif isinstance(description, BoundedIntOption):
                self.add_spinner_for(row, name, description)
            else:
                raise TypeError(f"Unhandled option type: {description}")

    def add_label(self, row: int, description: OptionDescription) -> None:
        text = description.text
        if description.detail is not None:
            wrapped = "<br />".join(textwrap.wrap(description.detail, width=55))
            text += f"<br /><strong>{wrapped}</strong>"
        label = QLabel(text)
        self.addWidget(label, row, 0)

    def add_checkbox_for(self, row: int, name: str, description: BooleanOption) -> None:
        def on_toggle(value: bool) -> None:
            if description.invert:
                value = not value
            self.settings.__dict__[name] = value

        checkbox = QCheckBox()
        value = self.settings.__dict__[name]
        if description.invert:
            value = not value
        checkbox.setChecked(value)
        checkbox.toggled.connect(on_toggle)
        self.addWidget(checkbox, row, 1, Qt.AlignRight)

    def add_combobox_for(self, row: int, name: str, description: ChoicesOption) -> None:
        combobox = QComboBox()

        def on_changed(index: int) -> None:
            self.settings.__dict__[name] = combobox.itemData(index)

        for text, value in description.choices.items():
            combobox.addItem(text, value)
        combobox.setCurrentText(
            description.text_for_value(self.settings.__dict__[name])
        )
        combobox.currentIndexChanged.connect(on_changed)
        self.addWidget(combobox, row, 1, Qt.AlignRight)

    def add_float_spin_slider_for(
        self, row: int, name: str, description: BoundedFloatOption
    ) -> None:
        spinner = FloatSpinSlider(
            description.min,
            description.max,
            self.settings.__dict__[name],
            divisor=description.divisor,
        )

        def on_changed() -> None:
            self.settings.__dict__[name] = spinner.value

        spinner.spinner.valueChanged.connect(on_changed)
        self.addLayout(spinner, row, 1, Qt.AlignRight)

    def add_spinner_for(
        self, row: int, name: str, description: BoundedIntOption
    ) -> None:
        def on_changed(value: int) -> None:
            self.settings.__dict__[name] = value

        spinner = QSpinBox()
        spinner.setMinimum(description.min)
        spinner.setMaximum(description.max)
        spinner.setValue(self.settings.__dict__[name])

        spinner.valueChanged.connect(on_changed)
        self.addWidget(spinner, row, 1, Qt.AlignRight)


class AutoSettingsGroup(QGroupBox):
    def __init__(self, page: str, section: str, settings: Settings) -> None:
        super().__init__(section)
        self.setLayout(AutoSettingsLayout(page, section, settings))


class AutoSettingsPageLayout(QVBoxLayout):
    def __init__(self, page: str, settings: Settings) -> None:
        super().__init__()
        self.setAlignment(Qt.AlignTop)

        for section in Settings.sections(page):
            self.addWidget(AutoSettingsGroup(page, section, settings))


class AutoSettingsPage(QWidget):
    def __init__(self, page: str, settings: Settings) -> None:
        super().__init__()
        self.setLayout(AutoSettingsPageLayout(page, settings))


class QSettingsWindow(QDialog):
    def __init__(self, game: Game):
        super().__init__()

        self.game = game
        self.pluginsPage = None
        self.pluginsOptionsPage = None

        self.pages: dict[str, AutoSettingsPage] = {}
        for page in Settings.pages():
            self.pages[page] = AutoSettingsPage(page, game.settings)

        self.setModal(True)
        self.setWindowTitle("Settings")
        self.setWindowIcon(CONST.ICONS["Settings"])
        self.setMinimumSize(600, 250)

        self.initUi()

    def initUi(self):
        self.layout = QGridLayout()

        self.categoryList = QListView()
        self.right_layout = QStackedLayout()

        self.categoryList.setMaximumWidth(175)

        self.categoryModel = QStandardItemModel(self.categoryList)

        self.categoryList.setIconSize(QSize(32, 32))

        for name, page in self.pages.items():
            page_item = QStandardItem(name)
            if name in CONST.ICONS:
                page_item.setIcon(CONST.ICONS[name])
            else:
                page_item.setIcon(CONST.ICONS["Generator"])
            page_item.setEditable(False)
            page_item.setSelectable(True)
            self.categoryModel.appendRow(page_item)
            self.right_layout.addWidget(page)

        self.initGeneratorLayout()
        generator = QStandardItem("Mission Generator")
        generator.setIcon(CONST.ICONS["Generator"])
        generator.setEditable(False)
        generator.setSelectable(True)
        self.categoryModel.appendRow(generator)
        self.right_layout.addWidget(self.generatorPage)

        self.initCheatLayout()
        cheat = QStandardItem("Cheat Menu")
        cheat.setIcon(CONST.ICONS["Cheat"])
        cheat.setEditable(False)
        cheat.setSelectable(True)
        self.categoryModel.appendRow(cheat)
        self.right_layout.addWidget(self.cheatPage)

        self.pluginsPage = PluginsPage()
        plugins = QStandardItem("LUA Plugins")
        plugins.setIcon(CONST.ICONS["Plugins"])
        plugins.setEditable(False)
        plugins.setSelectable(True)
        self.categoryModel.appendRow(plugins)
        self.right_layout.addWidget(self.pluginsPage)

        self.pluginsOptionsPage = PluginOptionsPage()
        pluginsOptions = QStandardItem("LUA Plugins Options")
        pluginsOptions.setIcon(CONST.ICONS["PluginsOptions"])
        pluginsOptions.setEditable(False)
        pluginsOptions.setSelectable(True)
        self.categoryModel.appendRow(pluginsOptions)
        self.right_layout.addWidget(self.pluginsOptionsPage)

        self.categoryList.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.categoryList.setModel(self.categoryModel)
        self.categoryList.selectionModel().setCurrentIndex(
            self.categoryList.indexAt(QPoint(1, 1)), QItemSelectionModel.Select
        )
        self.categoryList.selectionModel().selectionChanged.connect(
            self.onSelectionChanged
        )

        self.layout.addWidget(self.categoryList, 0, 0, 1, 1)
        self.layout.addLayout(self.right_layout, 0, 1, 5, 1)

        self.setLayout(self.layout)

    def init(self):
        pass

    def initGeneratorLayout(self):
        self.generatorPage = QWidget()
        self.generatorLayout = QVBoxLayout()
        self.generatorLayout.setAlignment(Qt.AlignTop)
        self.generatorPage.setLayout(self.generatorLayout)

        self.gameplay = QGroupBox("Gameplay")
        self.gameplayLayout = QGridLayout()
        self.gameplayLayout.setAlignment(Qt.AlignTop)
        self.gameplay.setLayout(self.gameplayLayout)

        self.supercarrier = QCheckBox()
        self.supercarrier.setChecked(self.game.settings.supercarrier)
        self.supercarrier.toggled.connect(self.applySettings)

        self.generate_marks = QCheckBox()
        self.generate_marks.setChecked(self.game.settings.generate_marks)
        self.generate_marks.toggled.connect(self.applySettings)

        self.generate_dark_kneeboard = QCheckBox()
        self.generate_dark_kneeboard.setChecked(
            self.game.settings.generate_dark_kneeboard
        )
        self.generate_dark_kneeboard.toggled.connect(self.applySettings)

        self.never_delay_players = QCheckBox()
        self.never_delay_players.setChecked(
            self.game.settings.never_delay_player_flights
        )
        self.never_delay_players.toggled.connect(self.applySettings)
        self.never_delay_players.setToolTip(
            "When checked, player flights with a delayed start time will be "
            "spawned immediately. AI wingmen may begin startup immediately."
        )

        self.desired_player_mission_duration = TimeInputs(
            "Desired mission duration",
            self.game.settings.desired_player_mission_duration,
        )
        self.desired_player_mission_duration.spinner.valueChanged.connect(
            self.applySettings
        )

        self.gameplayLayout.addWidget(QLabel("Use Supercarrier Module"), 0, 0)
        self.gameplayLayout.addWidget(self.supercarrier, 0, 1, Qt.AlignRight)
        self.gameplayLayout.addWidget(QLabel("Put Objective Markers on Map"), 1, 0)
        self.gameplayLayout.addWidget(self.generate_marks, 1, 1, Qt.AlignRight)

        dark_kneeboard_label = QLabel(
            "Generate Dark Kneeboard <br />"
            "<strong>Dark kneeboard for night missions.<br />"
            "This will likely make the kneeboard on the pilot leg unreadable.</strong>"
        )
        self.gameplayLayout.addWidget(dark_kneeboard_label, 2, 0)
        self.gameplayLayout.addWidget(self.generate_dark_kneeboard, 2, 1, Qt.AlignRight)
        self.gameplayLayout.addLayout(
            self.desired_player_mission_duration, 5, 0, Qt.AlignRight
        )

        spawn_players_immediately_tooltip = (
            "Always spawns player aircraft immediately, even if their start time is "
            "more than 10 minutes after the start of the mission. <strong>This does "
            "not alter the timing of your mission. Your TOT will not change. This "
            "option only allows the player to wait on the ground.</strong>"
        )
        spawn_immediately_label = QLabel(
            "Player flights ignore TOT and spawn immediately<br />"
            "<strong>Does not adjust package waypoint times.<br />"
            "Should not be used if players have runway or in-air starts.</strong>"
        )
        spawn_immediately_label.setToolTip(spawn_players_immediately_tooltip)
        self.gameplayLayout.addWidget(spawn_immediately_label, 3, 0)
        self.gameplayLayout.addWidget(self.never_delay_players, 3, 1, Qt.AlignRight)

        start_type_label = QLabel(
            "Default start type for AI aircraft<br /><strong>Warning: "
            "Options other than Cold will significantly reduce the<br />"
            "number of targets available for OCA/Aircraft missions,<br />"
            "and OCA/Aircraft flights will not be included in<br />"
            "automatically planned OCA packages.</strong>"
        )
        start_type_label.setToolTip(START_TYPE_TOOLTIP)
        start_type = StartTypeComboBox(self.game.settings)
        start_type.setCurrentText(self.game.settings.default_start_type)

        self.gameplayLayout.addWidget(start_type_label, 4, 0)
        self.gameplayLayout.addWidget(start_type, 4, 1)

        self.performance = QGroupBox("Performance")
        self.performanceLayout = QGridLayout()
        self.performanceLayout.setAlignment(Qt.AlignTop)
        self.performance.setLayout(self.performanceLayout)

        self.smoke = QCheckBox()
        self.smoke.setChecked(self.game.settings.perf_smoke_gen)
        self.smoke.toggled.connect(self.applySettings)

        self.smoke_spacing = QSpinBox()
        self.smoke_spacing.setMinimum(800)
        self.smoke_spacing.setMaximum(24000)
        self.smoke_spacing.setValue(self.game.settings.perf_smoke_spacing)
        self.smoke_spacing.valueChanged.connect(self.applySettings)

        self.red_alert = QCheckBox()
        self.red_alert.setChecked(self.game.settings.perf_red_alert_state)
        self.red_alert.toggled.connect(self.applySettings)

        self.arti = QCheckBox()
        self.arti.setChecked(self.game.settings.perf_artillery)
        self.arti.toggled.connect(self.applySettings)

        self.moving_units = QCheckBox()
        self.moving_units.setChecked(self.game.settings.perf_moving_units)
        self.moving_units.toggled.connect(self.applySettings)

        self.infantry = QCheckBox()
        self.infantry.setChecked(self.game.settings.perf_infantry)
        self.infantry.toggled.connect(self.applySettings)

        self.destroyed_units = QCheckBox()
        self.destroyed_units.setChecked(self.game.settings.perf_destroyed_units)
        self.destroyed_units.toggled.connect(self.applySettings)

        self.culling = QCheckBox()
        self.culling.setChecked(self.game.settings.perf_culling)
        self.culling.toggled.connect(self.applySettings)

        self.culling_distance = QSpinBox()
        self.culling_distance.setMinimum(10)
        self.culling_distance.setMaximum(10000)
        self.culling_distance.setValue(self.game.settings.perf_culling_distance)
        self.culling_distance.valueChanged.connect(self.applySettings)

        self.culling_do_not_cull_carrier = QCheckBox()
        self.culling_do_not_cull_carrier.setChecked(
            self.game.settings.perf_do_not_cull_carrier
        )
        self.culling_do_not_cull_carrier.toggled.connect(self.applySettings)

        self.performanceLayout.addWidget(
            QLabel("Smoke visual effect on frontline"), 0, 0
        )
        self.performanceLayout.addWidget(self.smoke, 0, 1, alignment=Qt.AlignRight)
        self.performanceLayout.addWidget(
            QLabel("Smoke generator spacing (higher means less smoke)"),
            1,
            0,
            alignment=Qt.AlignRight,
        )
        self.performanceLayout.addWidget(
            self.smoke_spacing, 1, 1, alignment=Qt.AlignRight
        )
        self.performanceLayout.addWidget(QLabel("SAM starts in RED alert mode"), 2, 0)
        self.performanceLayout.addWidget(self.red_alert, 2, 1, alignment=Qt.AlignRight)
        self.performanceLayout.addWidget(QLabel("Artillery strikes"), 3, 0)
        self.performanceLayout.addWidget(self.arti, 3, 1, alignment=Qt.AlignRight)
        self.performanceLayout.addWidget(QLabel("Moving ground units"), 4, 0)
        self.performanceLayout.addWidget(
            self.moving_units, 4, 1, alignment=Qt.AlignRight
        )
        self.performanceLayout.addWidget(
            QLabel("Generate infantry squads along vehicles"), 5, 0
        )
        self.performanceLayout.addWidget(self.infantry, 5, 1, alignment=Qt.AlignRight)
        self.performanceLayout.addWidget(
            QLabel("Include destroyed units carcass"), 6, 0
        )
        self.performanceLayout.addWidget(
            self.destroyed_units, 6, 1, alignment=Qt.AlignRight
        )

        self.performanceLayout.addWidget(QHorizontalSeparationLine(), 7, 0, 1, 2)
        self.performanceLayout.addWidget(
            QLabel("Culling of distant units enabled"), 8, 0
        )
        self.performanceLayout.addWidget(self.culling, 8, 1, alignment=Qt.AlignRight)
        self.performanceLayout.addWidget(QLabel("Culling distance (km)"), 9, 0)
        self.performanceLayout.addWidget(
            self.culling_distance, 9, 1, alignment=Qt.AlignRight
        )
        self.performanceLayout.addWidget(
            QLabel("Do not cull carrier's surroundings"), 10, 0
        )
        self.performanceLayout.addWidget(
            self.culling_do_not_cull_carrier, 10, 1, alignment=Qt.AlignRight
        )

        self.generatorLayout.addWidget(self.gameplay)
        self.generatorLayout.addWidget(
            QLabel(
                "Disabling settings below may improve performance, but will impact the overall quality of the experience."
            )
        )
        self.generatorLayout.addWidget(self.performance)

    def initCheatLayout(self):

        self.cheatPage = QWidget()
        self.cheatLayout = QVBoxLayout()
        self.cheatPage.setLayout(self.cheatLayout)

        self.cheat_options = CheatSettingsBox(self.game, self.applySettings)
        self.cheatLayout.addWidget(self.cheat_options)

        self.moneyCheatBox = QGroupBox("Money Cheat")
        self.moneyCheatBox.setAlignment(Qt.AlignTop)
        self.moneyCheatBoxLayout = QGridLayout()
        self.moneyCheatBox.setLayout(self.moneyCheatBoxLayout)

        cheats_amounts = [25, 50, 100, 200, 500, 1000, -25, -50, -100, -200]
        for i, amount in enumerate(cheats_amounts):
            if amount > 0:
                btn = QPushButton("Cheat +" + str(amount) + "M")
                btn.setProperty("style", "btn-success")
            else:
                btn = QPushButton("Cheat " + str(amount) + "M")
                btn.setProperty("style", "btn-danger")
            btn.clicked.connect(self.cheatLambda(amount))
            self.moneyCheatBoxLayout.addWidget(btn, i / 2, i % 2)
        self.cheatLayout.addWidget(self.moneyCheatBox, stretch=1)

    def cheatLambda(self, amount):
        return lambda: self.cheatMoney(amount)

    def cheatMoney(self, amount):
        logging.info("CHEATING FOR AMOUNT : " + str(amount) + "M")
        self.game.blue.budget += amount
        GameUpdateSignal.get_instance().updateGame(self.game)

    def applySettings(self):
        self.game.settings.player_skill = CONST.SKILL_OPTIONS[
            self.playerCoalitionSkill.currentIndex()
        ]
        self.game.settings.enemy_skill = CONST.SKILL_OPTIONS[
            self.enemyCoalitionSkill.currentIndex()
        ]
        self.game.settings.enemy_vehicle_skill = CONST.SKILL_OPTIONS[
            self.enemyAASkill.currentIndex()
        ]
        self.game.settings.player_income_multiplier = self.player_income.value
        self.game.settings.enemy_income_multiplier = self.enemy_income.value
        self.game.settings.manpads = self.manpads.isChecked()
        self.game.settings.labels = CONST.LABELS_OPTIONS[
            self.difficultyLabel.currentIndex()
        ]
        self.game.settings.night_disabled = self.noNightMission.isChecked()
        self.game.settings.map_coalition_visibility = (
            self.mapVisibiitySelection.currentData()
        )
        self.game.settings.external_views_allowed = self.ext_views.isChecked()
        self.game.settings.battle_damage_assessment = (
            self.battleDamageAssessment.currentData()
        )
        self.game.settings.generate_marks = self.generate_marks.isChecked()
        self.game.settings.never_delay_player_flights = (
            self.never_delay_players.isChecked()
        )

        self.game.settings.supercarrier = self.supercarrier.isChecked()

        self.game.settings.generate_dark_kneeboard = (
            self.generate_dark_kneeboard.isChecked()
        )

        self.game.settings.desired_player_mission_duration = (
            self.desired_player_mission_duration.value
        )

        self.game.settings.perf_red_alert_state = self.red_alert.isChecked()
        self.game.settings.perf_smoke_gen = self.smoke.isChecked()
        self.game.settings.perf_smoke_spacing = self.smoke_spacing.value()
        self.game.settings.perf_artillery = self.arti.isChecked()
        self.game.settings.perf_moving_units = self.moving_units.isChecked()
        self.game.settings.perf_infantry = self.infantry.isChecked()
        self.game.settings.perf_destroyed_units = self.destroyed_units.isChecked()

        self.game.settings.perf_culling = self.culling.isChecked()
        self.game.settings.perf_culling_distance = int(self.culling_distance.value())
        self.game.settings.perf_do_not_cull_carrier = (
            self.culling_do_not_cull_carrier.isChecked()
        )

        self.game.settings.show_red_ato = self.cheat_options.show_red_ato
        self.game.settings.enable_frontline_cheats = (
            self.cheat_options.show_frontline_cheat
        )
        self.game.settings.enable_base_capture_cheat = (
            self.cheat_options.show_base_capture_cheat
        )

        self.game.compute_conflicts_position()
        GameUpdateSignal.get_instance().updateGame(self.game)

    def onSelectionChanged(self):
        index = self.categoryList.selectionModel().currentIndex().row()
        self.right_layout.setCurrentIndex(index)
