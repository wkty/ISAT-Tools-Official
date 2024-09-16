![IAST Tool Image](https://github.com/wkty/ISAT-Tools-Official/blob/main/appendix/iast_img.png)
<div align="center">

# ISAT-Tools-Official  
ISAT 排放清单处理工具

</div>

---

**(2024.09 Update)**  
**(2024.09 更新说明)**

---

## New Features  
## 新特性

<table>
  <tbody>
    <tr>
      <td>
        <ul>
          <li>More flexible spatial allocation functionality</li>
          <li>更灵活的空间分配功能</li>
        </ul>
      </td>
    </tr>
    <tr>
      <td>
        <ul>
          <li>Faster model output results</li>
          <li>更快速的模型输出结果</li>
        </ul>
      </td>
    </tr>
    <tr>
      <td>
        <ul>
          <li>Complete emission inventory processing chain</li>
          <li>全链条的清单处理流程</li>
        </ul>
      </td>
    </tr>
  </tbody>
</table>

---

### 1. More Flexible Spatial Allocation Functionality  
### 1. 更灵活的空间分配功能

This update integrates the original "downscale" and "mapinv" modules into a new "Spatialallocator" module, allowing more flexible regional emissions inventory downscaling and spatial allocation functions.  
本次更新重新整合了原有的“downscale”模块与“mapinv”模块，并生成新的“Spatialallocator”模块，使得用户可以更加灵活地完成区域排放清单降尺度以及本地排放清单空间分配的功能。

![img1](https://raw.githubusercontent.com/wkty/ISAT-Tools-Official/main/appendix/update1/img1.jpg)  
<div align="center">Figure 1: New Feature Diagram  
图1: 新功能示意图</div>

The new module supports raster files (TIFF, ASC, ADF), point files (CSV), line vector files (SHP), and grid area as spatial allocation factors.  
新模块支持栅格文件（包括 TIFF 格式、ASC 格式、ADF 格式）、点文件（CSV 文件）、线矢量文件（SHP 文件）以及网格面积为空间分配因子的空间分配功能。

#### Example Configuration  
#### 配置文件示例

| **\[Domain\]** | **区域设定参数** |
| --- | --- |
| target:./input/domain/aqm_hb9km.shp | Target grid vector | 目标网格矢量 |
| region:./input/domain/Hebei.shp | Regional vector file | 区域矢量文件 |
| poplist:PM25,SO2,NOx,VOCs,CO,NH3,BC,OC,PMC | Species list | 物种列表 |
| exclude_on:True | Exclude region on/off | 是否开启区域抠除 |
| region_ex:./input/domain/Hebei.shp | Excluded region vector | 抠除区域矢量 |

---

### 2. Faster Model Output Results  
### 2. 更快速的模型输出结果

The focus of this update is on optimizing the code for generating CMAQ/CAMx emission inventories in Prepmodel, significantly speeding up the process.  
本次更新重点优化了 Prepmodel 中的 CMAQ/CAMx 排放清单生成代码，大幅提升了生成效率。

For example, generating an emission inventory for over 100,000 point sources for a simulation duration of 760 hours now takes about 2 minutes.  
例如，针对超过 10 万个点源，准备 760 小时的排放清单文件，耗时约 2 分钟。

![img2](https://raw.githubusercontent.com/wkty/ISAT-Tools-Official/main/appendix/update1/img2.jpg)  
<div align="center">Figure 2: Point Source Chimney Information File  
图2: 点源烟囱信息文件</div>

The point source emission files can be generated in about 1 minute.  
点源排放文件生成时间约为 1 分钟。

![img3](https://raw.githubusercontent.com/wkty/ISAT-Tools-Official/main/appendix/update1/img3.jpg)

---

### 3. Complete Emission Inventory Processing Chain  
### 3. 全链条的清单处理流程

<table>
  <tbody>
    <tr>
      <th><strong>Module Name</strong></th>
      <th><strong>Module Function</strong></th>
    </tr>
    <tr>
      <td><p>Prepgrid</p></td>
      <td>
        <ul>
          <li>For grid preparation of study area</li>
          <li>用于研究区域网格化</li>
          <li>Supports WRF model namelist.input configuration</li>
          <li>支持 WRF 模型 namelist.input 配置</li>
        </ul>
      </td>
    </tr>
    <tr>
      <td><p>Spatialallocator</p></td>
      <td>
        <ul>
          <li>For local and regional emissions inventory allocation</li>
          <li>用于本地和区域排放清单分配</li>
        </ul>
      </td>
    </tr>
    <tr>
      <td><p>Prepmodel</p></td>
      <td>
        <ul>
          <li>Generates inline format emissions for CMAQ/CAMx</li>
          <li>生成 CMAQ/CAMx 可用的 inline 格式排放清单</li>
        </ul>
      </td>
    </tr>
  </tbody>
</table>

---

<div align="center">

![img4](https://raw.githubusercontent.com/wkty/ISAT-Tools-Official/main/appendix/update1/img4.jpg)

Follow WeChat Official Account: "Energy-Matter-Carbon-Nexus"  
欢迎关注“能-物-碳-污 Nexus”公众号

</div>
