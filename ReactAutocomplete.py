import sublime, sublime_plugin

import re
import os

from . import parse_methods

MIN_WORD_SIZE = 4
MAX_WORD_SIZE = 50

SETTINGS = {
  "file_extensions": [".cjsx", ".jsx", ".js"],
  "output_format": "cjsx" # cjsx, jsx
}


class AddRequireCommand(sublime_plugin.TextCommand):
  def run(self, edit, component):
    check_pattern = u"{} \= require".format(component["display_name"])
    if not self.view.find(check_pattern, 0):
      path = re.sub('\.cjsx$', '', component["path"])
      path = re.sub(".*?src\/scripts\/", "", path)

      if SETTINGS["output_format"] == "cjsx":
        require_text = "\n{} = require '{}'\n".format(component["display_name"], path)
      else:
        require_text = "\n{} = require('{}');\n".format(component["display_name"], path)

      all_requires = self.view.find_all("[a-zA-Z]* \= require", 0)
      if all_requires:
        insert_at = self.view.line(all_requires[-1]).end()
      else:
        insert_at = self.view.line(0).end()

      self.view.insert(edit, insert_at, require_text)

class ReactAutocomplete(sublime_plugin.EventListener):
  """
  Provide component name completions for Builder
  """
  def __init__(self):
    self.components = {}
    self.component_names = []
    self.component_name_suggestions = []
    self.initial_autocomplete_point = None

  def on_load(self, view):
    self.preload_files(view)

  def find_settings_file(self, view):
    folders = os.path.dirname(view.file_name()).split("/")
    settings_path = None
    for folder in reversed(folders):
      path = '/'.join(folders)
      is_file = os.path.isfile(os.path.join(path,".react-autocomplete"))
      if is_file:
        settings_path = os.path.join(path,".react-autocomplete")
        break
      del folders[-1]

    return settings_path

  def get_component_folder(self, settings_file):
    with open(settings_file, 'r', encoding="utf-8") as f:
      settings_file_contents = f.read()
      component_folder = os.path.join(os.path.dirname(settings_file), settings_file_contents.rstrip("\n"))

      return component_folder

  def preload_files(self, view):
    self.components = {}
    self.component_names = []
    self.component_name_suggestions = []

    settings_file = self.find_settings_file(view)

    if settings_file:
      component_folder = self.get_component_folder(settings_file)
    else:
      return

    for root, dirs, files in os.walk(component_folder, topdown=False):
      for name in files:
        filename, file_extension = os.path.splitext(name)
        if not file_extension in SETTINGS["file_extensions"]:
          continue

        with open(os.path.join(root, name), 'r', encoding='utf-8') as f:
          component_info = get_file_info(f)

          suggestion = {
            "title": "{} \t {}".format(component_info["display_name"], name),
            "suggestion": "" + component_info["display_name"] + "\n" + self.get_prop_string(component_info["props"]) + "/>"
          }

          self.components[component_info["display_name"]] = {
            "suggestion": suggestion,
            "props": component_info["props"],
            "display_name": component_info["display_name"],
            "path": os.path.join(root, name)
          }

          self.component_names.append(component_info["display_name"])
          self.component_names.sort()

    self.component_name_suggestions = [(self.components[name]["suggestion"]["title"], self.components[name]["suggestion"]["suggestion"]) for name in self.component_names]

  def get_prop_string(self, props):
    prop_string = ""
    for prop in props:
      # if prop["required"]:
      prop_string = prop_string + "  " + prop["name"] + "={###" + prop["type"] + "###}\n"
    return prop_string

  """
  Runs when the file is modified
  """
  def on_modified(self, view):
    if self.initial_autocomplete_point:
      component_name = (view.substr(view.word(self.initial_autocomplete_point)))
      if component_name in self.components:
        view.run_command("add_require", {"component": self.components[component_name]})
        self.initial_autocomplete_point = None

  """
  Runs when user starts typing
  """
  def on_query_completions(self, view, prefix, locations):
    self.preload_files(view)
    self.initial_autocomplete_point = None

    if view.match_selector(locations[0], "jsx.tag-area.coffee"):
      self.initial_autocomplete_point = locations[0] - len(prefix)
      cursor_start = locations[0] - len(prefix) - 1
      is_start_of_component = view.substr(sublime.Region(cursor_start, cursor_start + 1)) == "<"

      if is_start_of_component:
        return self.component_name_suggestions
      else:
        # we want to get list of available props for current component
        start = locations[0] - len(prefix)

        start_of_component = view.find_by_class(start, False, sublime.CLASS_PUNCTUATION_END, "<")
        component_name = view.substr(view.word(start_of_component))

        sugs = []
        if component_name in self.components:
          sugs = [("{} \t {} \t {}".format(prop["name"], prop["type"], prop["is_required"]), "{}={}".format(prop["name"], "{}")) for prop in self.components[component_name]["props"]]

        return sugs

    else:
      return []
