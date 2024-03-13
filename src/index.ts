import { ExtensionContext, window, workspace } from 'coc.nvim';

const channel = window.createOutputChannel('vim-options');

export async function activate(context: ExtensionContext): Promise<void> {
  updateOptions();
  context.subscriptions.push(
    workspace.registerAutocmd({
      event: 'FileType',
      callback: async () => {
        channel.appendLine('filetype changed: updating options');
        await updateOptions();
      },
    })
  );
}

async function getOptionsManagedByEditorConfig(): Promise<string[]> {
  const editorConfig = await (await workspace.nvim.buffer).getVar('editorconfig');
  if (editorConfig == null) return [];

  const EDITORCONFIG_OPTION_MAP = {
    charset: ['bomb', 'fileencoding'],
    end_of_line: ['fileformat'],
    indent_style: ['expandtab'],
    indent_size: ['shiftwidth', 'softtabstop'],
    insert_final_newline: ['fixendofline', 'endofline'],
    max_line_length: ['textwidth'],
    tab_width: ['tabstop'],
  };

  const options: string[] = [];
  for (const property in EDITORCONFIG_OPTION_MAP) {
    if (editorConfig[property]) {
      options.push(...EDITORCONFIG_OPTION_MAP[property]);
    }
  }

  return options;
}

async function updateOptions(): Promise<void> {
  const buffer = await workspace.nvim.buffer;
  const doc = await workspace.document;
  channel.appendLine(`buffer id: ${buffer.id}; language: ${doc.textDocument.languageId}`);
  // @ts-ignore: type definition for workspace.getConfiguration() is old
  const config = workspace.getConfiguration('vim-options', doc);
  const editorConfigOptions = await getOptionsManagedByEditorConfig();
  channel.appendLine('Config: ' + JSON.stringify(config));
  channel.appendLine('EditorConfig: ' + JSON.stringify(editorConfigOptions));

  for (const option in config) {
    if (editorConfigOptions.includes(option)) {
      channel.appendLine(`ignore: ${option}; keep EditorConfig value as is`);
      continue;
    }

    try {
      await buffer.setOption(option, config[option]);
      channel.appendLine(`set: ${option} => ${await buffer.getOption(option)}`);
    } catch (e) {
      channel.appendLine(`FAILED: set ${option}; reason: {e}`);
    }
  }
}
