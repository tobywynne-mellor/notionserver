from notion.block import CodeBlock, ColumnListBlock, ColumnBlock, TextBlock

class PostProcessor:

  def process(self, entry, processorType):
    processor = self._get_proccessor(processorType)
    return processor(entry)
  
  def _get_proccessor(self, processorType):
    if processorType == "Coding Problems":
      return self._process_coding_problem
    else:
      raise ValueError(processorType)
  
  def _process_coding_problem(self, entry):
    # add difficulty
    entry.difficulty = self._get_difficulty(entry.name)

    # fix name
    start = entry.name.index(": Problem") + 2
    end = entry.name.index("[")
    entry.name = entry.name[start:end]
    
    # clean quesiton content
    # will be text block
    content = self._clean_text(entry.children[0].title)

    for kid in entry.children:
      kid.remove()
    
    col_list = entry.children.add_new(ColumnListBlock)
    col1 = col_list.children.add_new(ColumnBlock)
    col2 = col_list.children.add_new(ColumnBlock)
    col1.children.add_new(
        TextBlock, title=content
    )
    col2.children.add_new(
      CodeBlock, title="# Solution goes here..."
    )

  def _get_difficulty(self, name):
    if "Easy" in name:
      return "Easy"
    elif "Medium" in name:
      return "Medium"
    elif "Hard" in name:
      return "Hard"
    else:
      raise NameError(name)

  def _clean_text(self, text):
    dashes = "".join(['-'] * 80)
    end = text.index(dashes)
    start = text.index('\n')
    return text[start:end]