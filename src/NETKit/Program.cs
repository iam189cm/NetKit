using NETKit.UI.Forms;
using NETKit.Common;

namespace NETKit
{
    internal static class Program
    {
        /// <summary>
        /// 应用程序的主入口点
        /// </summary>
        [STAThread]
        static void Main()
        {
            // 配置应用程序设置
            ApplicationConfiguration.Initialize();
            
            // 设置应用程序标题
            Application.SetCompatibleTextRenderingDefault(false);
            
            try
            {
                // 启动主窗体
                Application.Run(new MainForm());
            }
            catch (Exception ex)
            {
                MessageBox.Show(
                    $"应用程序启动失败: {ex.Message}",
                    Constants.Application.DisplayName,
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error);
            }
        }
    }
}
