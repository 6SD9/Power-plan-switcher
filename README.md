# Power-plan-switcher
A super-lightweight background utility that automatically switches Windows power plans. Its purpose is to control CPU frequency in temperature- or noise-sensitive scenarios.<br></br>
这是一个超轻量自动切换windows电源的后台软件。目的是在温度或者噪音敏感场景控制cpu频率。<br></br>
### Five levels/五种档位
- Disabled/停用
- Disable CPU Turbo Boost/关闭CPU睿频
- Medium frequency/中频率
- Higher frequency/较高频率
- Unlimited/无限制 <br></br>
The system monitors all configured target processes that are running and selects the highest-priority power plan as the active plan.<br></br>
系统会同时检测所有运行的目标进程选择最高等级的电源计划作为当前目标

## Usage/使用
#### Power plan “Disable Turbo Boost”/电源计划“关闭睿频”
1. Create a new power plan named Disable Turbo Boost: Control Panel → Power Options → Create a power plan.<br></br>新建电源计划“关闭睿频”：控制面板 → 电源选项 → 创建电源计划<br></br>
2. Edit the plan: Control Panel → Power Options → click Disable Turbo Boost → Change plan settings → Change advanced power settings.<br></br>设置电源计划：控制面板 → 电源选项 → 点击“关闭睿频”更改计划设置 → 更改高级电源设置<br></br>
3. Under Processor power management, disable Processor boost mode (or Turbo Boost).<br></br>处理器电源管理：禁用处理器提升模式<br></br>
4. Save<br></br>保存

#### Power plan “Medium / Higher frequency”/电源计划中高频率
1. Create and name a power plan, then open Change advanced power settings → Processor power management.<br></br>同样建立电源计划并命名，然后到更改高级电源设置的处理器电源管理<br></br>
2. Adjust the Maximum processor frequency, Processor power efficiency (class 1), and other processor frequency-related values to suit your needs.<br></br>调整处理器最大频率、第1类处理器电源效率和处理器最大频率的数值到自己的要求数值<br></br>
3. Save<br></br>保存

#### 获得电源计划的guid
In a command prompt run:
```
powercfg /list
```

#### Configure the software/配置软件
1. Run the program (either the .py file or the executable in the folder).<br></br>运行程序(可以用py文件，也可以使用目录下的exe直接运行)<br></br>
2. Right-click the tray icon and choose Settings.<br></br>在系统托盘中右键小图标选择setting<br></br>
3. Enter the plan GUID(s) and the processes whose CPU frequency you want the software to control.<br></br>填入guid和所需控制频率的进程
```
Operation logic:
The system monitors all configured target processes that are running and selects the highest-priority power plan as the current target.
运行逻辑
系统会同时检测所有运行的目标进程选择最高等级的电源计划作为当前目标
```
