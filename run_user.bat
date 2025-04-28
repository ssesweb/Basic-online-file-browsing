@echo off
chcp 65001 > nul

title 文件浏览服务启动器

:MENU
cls
echo.
echo  ***************************************************
echo  *                文件浏览服务启动器                *
echo  ***************************************************
echo.
echo 请选择启动模式：
echo.
echo   1. 开发模式 (适合调试，输出更多日志)
echo   -
echo   2. 生产模式 (适合正式使用，更稳定)
echo   -
echo   3. 退出
echo.
set /p "mode=请输入数字选择模式 (默认 2): "

if "%mode%"=="" (
    set "mode=2"
)

if "%mode%"=="1" (
    echo 正在以开发模式启动...
    call run_dev.bat
    goto END
) else if "%mode%"=="2" (
    echo 正在以生产模式启动...
    call run_prod.bat
    goto END
) else if "%mode%"=="3" (
    echo 退出程序...
    goto EXIT
) else (
    echo.
    echo 你他妈输错了！请重新选择。
    pause
    goto MENU
)

:END
echo.
echo 启动完成！请在浏览器中访问：
echo http://localhost:5000
echo.
pause

:EXIT
exit
