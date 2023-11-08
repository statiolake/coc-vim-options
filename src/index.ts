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

async function updateOptions(): Promise<void> {
  const buffer = await workspace.nvim.buffer;
  const doc = workspace.getDocument(buffer.id);
  const config = workspace.getConfiguration('vim-options', doc);
  channel.appendLine(JSON.stringify(config));
  for (const option in config) {
    await buffer.setOption(option, config[option]);
    channel.appendLine(`set: ${option} => ${await buffer.getOption(option)}`);
  }
}
