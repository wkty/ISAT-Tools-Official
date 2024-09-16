![IAST Tool Image](https://github.com/wkty/ISAT-Tools-Official/blob/main/appendix/iast_img.png)
<div align="center">

# ISAT-Tools-Official
ISAT 排放清单处理工具


</div>


（2024.09更新说明）

<table>
  <tbody>
    <tr>
      <td>
        <ul>
          <li>更灵活的空间分配功能</li>
        </ul>
      </td>
    </tr>
    <tr>
      <td>
        <ul>
          <li><a id="_Hlk177068140"></a>更快速的模型输出结果</li>
        </ul>
      </td>
    </tr>
    <tr>
      <td>
        <ul>
          <li>全链条的清单处理流程</li>
        </ul>
      </td>
    </tr>
  </tbody>
</table>

1. 更灵活的空间分配功能

本次更新重新整合了原有的“downscale”模块与“mapinv”模块，并生成新的“Spatialallocator”模块，使得用户可以更加灵活地完成区域排放清单降尺度以及本地排放清单空间分配的功能，以满足碳污排放清单网格化以及处理空气质量模型排放清单等需求。
![img1](https://github.com/wkty/ISAT-Tools-Official/blob/main/appendix/%E5%9B%BE%E7%89%871.jpg)
<div align="center">
图1 新功能示意图
</div>

新模块支持栅格文件（包括tiff格式、asc格式、adf格式）、点文件（csv文件）、线矢量文件（shpfile文件）以及网格面积为空间分配因子的空间分配功能。由此，新模块的配置文件（par.ini）也分为区域划定（\[Domain\]）、空间分配因子参数（\[R_Proxy\]、\[P_Proxy\]、\[L_Proxy\]、\[A_Proxy\]），案例如下：

| **\[Domain\]** | **区域设定参数** |
| --- | --- |
| target:./input/domain/aqm_hb9km.shp | 目标网格矢量 |
| region:./input/domain/Hebei.shp | 区域矢量文件 |
| poplist:PM25,SO2,NOx,VOCs,CO,NH3,BC,OC,PMC | 物种列表 |
| exclude_on:True | 是否开启区域抠除 |
| region_ex:./input/domain/Hebei.shp | 抠除区域矢量 |
| **\[R_Proxy\]** | **栅格文件参数** |
| raster_on:True | 是否使用栅格文件 |
| rasterpath:./input/SA/Popraster/ | 栅格文件路径 |
| inputinv_r:./input/Emis/AR.csv | 排放清单文件 |
| outname_r:AR | 输出文件标签 |
| **\[P_Proxy\]** | **点文件参数** |
| point_on:True | 是否使用点文件 |
| pointpath:./input/SA/Pointcsv/neighborhood.csv | 点文件路径 |
| key:weight | 点文件权重名称 |
| inputinv_p:./input/Emis/CY.csv | 排放清单文件 |
| outname_p:CY | 输出文件标签 |
| **\[L_Proxy\]** | **线文件参数** |
| line_on:NTrue | 是否使用线文件 |
| linepath:./input/SA/Lineshp/nationalroads.shp | 线文件路径 |
| lineref:./input/SA/Lineshp/lineweight.csv | 线文件权重 |
| inputinv_l:./input/Emis/transport.csv | 排放清单文件 |
| outname_l:LINE_TR | 输出文件标签 |
| **\[A_Proxy\]** | **面积参数设定** |
| area_on:NTrue | 是否使用面积插值 |
| inputinv_a:./input/Emis/residential.csv | 清单文件 |
| outname_a:AREA_RES | 输出文件标签 |

二、更快速的模型输出结果

本次更新重点优化了Prepmodel中的CMAQ/CAMx排放清单生成代码，避免了生成清单文件过程较慢的问题。如下面这个案例中，针对超过10余万个点源的17类点源排放源，准备模拟时长为760小时的排放清单文件耗时约2分钟，显著快于原程序耗时。

1. 点源烟囱信息文件1秒内生成

![img2](https://github.com/wkty/ISAT-Tools-Official/blob/main/appendix/%E5%9B%BE%E7%89%872.jpg)

（2）点源排放文件1分钟左右生成

![img3](https://github.com/wkty/ISAT-Tools-Official/blob/main/appendix/%E5%9B%BE%E7%89%873.jpg)<br>
三、全链条的清单处理流程

<table><tbody><tr><th><p><strong>模块名称</strong></p></th><th><p><strong>模块功能</strong></p></th></tr><tr><td><p>Prepgrid</p></td><td><ul><li>用于研究区域网格化</li><li>可基于WRF/AQM嵌套规则获取多重网格参数</li><li>输出结果可支持WRF模型namelist.input配置</li></ul></td></tr><tr><td><p>Spatialallocator</p></td><td><ul><li>可用于本地清单分配，满足碳污融合清单网格化等工作</li><li>可用于区域清单分配，满足获取本地排放清单以外区域的网格化排放量，满足空气质量模型排放清单文件准备等使用场景</li></ul></td></tr><tr><td><p>Prepmodel</p></td><td><ul><li>可完成时间分配、物种分配、空间分配，生成CMAQ/CAMx可用的inline格式排放清单</li><li>灵活的物种分配文件格式：可满足用户在CMAQ模型中新增化学物种时，生成相应的排放清单文件</li></ul></td></tr></tbody></table>
<div align="center">

![img4](https://github.com/wkty/ISAT-Tools-Official/blob/main/appendix/%E5%9B%BE%E7%89%874.jpg)

欢迎关注“能-物-碳-污 Nexus”公众号

获取新版ISAT排放清单处理工具
</div>
