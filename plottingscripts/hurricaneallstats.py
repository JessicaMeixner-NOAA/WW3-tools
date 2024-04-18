import numpy as np
import matplotlib.pyplot as plt

from emcpy.plots.plots import LinePlot
from emcpy.plots.create_plots import CreatePlot, CreateFigure



day=[1., 2., 3., 4., 5., 6., 7.]
count_HR3a_hurricane_JASON3=[10198040., 10192653., 10191803., 10191802., 10190093., 10106586., 10111226.]
bias_hs_HR3a_hurricane_JASON3=[0.32394449, 0.34760022, 0.36173546, 0.37663709, 0.38687284, 0.40035834, 0.40617765]
bias_wnd_HR3a_hurricane_JASON3=[5.02740503, 5.22818242, 5.24282067, 5.26891086, 5.26775979, 5.27555695, 5.26884804]
rmse_hs_HR3a_hurricane_JASON3=[0.95192063, 0.96917614, 0.99888237, 1.04690042, 1.1024982 , 1.17451675, 1.24340137]
rmse_wnd_HR3a_hurricane_JASON3=[5.72540145, 5.87935087, 5.93539416, 6.02418333, 6.08343427, 6.13687947, 6.18506821]

bias_hs_HR3b_hurricane_JASON3=[0.32452008, 0.34806179, 0.36198393, 0.37637549, 0.38552648, 0.3981101 , 0.40215822]
bias_wnd_HR3b_hurricane_JASON3=[5.02974649, 5.23255561, 5.24865853, 5.2732597 , 5.2736001 , 5.27424699, 5.26345299]
rmse_hs_HR3b_hurricane_JASON3=[0.95196171, 0.9689082 , 0.99763951, 1.04444761, 1.10077488, 1.17266037, 1.23738522]
rmse_wnd_HR3b_hurricane_JASON3=[5.72543122, 5.87850813, 5.93474533, 6.02181686, 6.08426279, 6.12806026, 6.17297656]

bias_hs_multi1_hurricane_JASON3=[0.06315162, 0.06246363, 0.05947509, 0.06080007, 0.06303546, 0.0649572 , 0.06108136]
bias_wnd_multi1_hurricane_JASON3=[-0.68313358, -0.69508772, -0.7021419 , -0.69486074, -0.69030066, -0.69824777, -0.72455189]
rmse_hs_multi1_hurricane_JASON3=[0.41003308, 0.43999372, 0.50332841, 0.60503645, 0.72202615, 0.83765748, 0.94870672]
rmse_wnd_multi1_hurricane_JASON3=[1.58837952, 1.81239985, 2.10906147, 2.45144141, 2.79493869, 3.11226404, 3.40995389]


bias_hs_GFSv16_hurricane_JASON3=[-0.37550323, -0.2802998 , -0.23511494, -0.20041004, -0.17357427, -0.1454663 , -0.12566124]
bias_wnd_GFSv16_hurricane_JASON3=[5.12885427, 5.10620694, 5.10870633, 5.13520149, 5.15913101, 5.18520918, 5.20232087]
rmse_hs_GFSv16_hurricane_JASON3=[0.79881666, 0.60035556, 0.57144972, 0.61602525, 0.70297727, 0.80153465, 0.91348285]
rmse_wnd_GFSv16_hurricane_JASON3=[5.77253611, 5.7896487 , 5.83602417, 5.92456624, 6.02141101, 6.09144774, 6.17342949]

bias_hs_HR1_hurricane_JASON3=[-0.17308536, -0.14833392, -0.13567134, -0.12277987, -0.11271387, -0.10265468, -0.10082836]
bias_wnd_HR1_hurricane_JASON3=[4.64407696, 5.15810388, 5.16061436, 5.18025997, 5.18915037, 5.19114003, 5.17220726]
rmse_hs_HR1_hurricane_JASON3=[0.38926081, 0.3864838 , 0.43640465, 0.52404726, 0.63236554, 0.75241065, 0.8638259 ]
rmse_wnd_HR1_hurricane_JASON3=[5.48907091, 5.79438446, 5.83705418, 5.91733188, 5.99254046, 6.05565197, 6.099571  ]

bias_hs_HR2_hurricane_JASON3=[-0.16529931, -0.13124813, -0.11326679, -0.09649088, -0.08520506, -0.07409622, -0.06783679]
bias_wnd_HR2_hurricane_JASON3=[4.6769323 , 5.20026674, 5.20626741, 5.2274648 , 5.22893708, 5.22771574, 5.22166033]
rmse_hs_HR2_hurricane_JASON3=[0.38709924, 0.38355969, 0.43554913, 0.52686032, 0.63308998, 0.75352441, 0.86959335]
rmse_wnd_HR2_hurricane_JASON3=[5.52838862, 5.84136739, 5.88946339, 5.974001  , 6.03985977, 6.10502246, 6.16558376]

lprmse_hs_multi1_hurricane_JASON3 = LinePlot(day, rmse_hs_multi1_hurricane_JASON3)
lprmse_hs_GFSv16_hurricane_JASON3 = LinePlot(day, rmse_hs_GFSv16_hurricane_JASON3)
lprmse_hs_HR1_hurricane_JASON3 = LinePlot(day, rmse_hs_HR1_hurricane_JASON3)
lprmse_hs_HR2_hurricane_JASON3 = LinePlot(day, rmse_hs_HR2_hurricane_JASON3)
lprmse_hs_HR3a_hurricane_JASON3 = LinePlot(day, rmse_hs_HR3a_hurricane_JASON3)
lprmse_hs_HR3b_hurricane_JASON3 = LinePlot(day, rmse_hs_HR3b_hurricane_JASON3)

lprmse_hs_multi1_hurricane_JASON3.color = 'tab:orange'
lprmse_hs_GFSv16_hurricane_JASON3.color = 'tab:blue'
lprmse_hs_HR1_hurricane_JASON3.color = 'tab:green'
lprmse_hs_HR2_hurricane_JASON3.color = 'tab:red'
lprmse_hs_HR3a_hurricane_JASON3.color = 'tab:purple'
lprmse_hs_HR3b_hurricane_JASON3.color = 'tab:pink'

lprmse_hs_multi1_hurricane_JASON3 = 'multi 1'
lprmse_hs_GFSv16_hurricane_JASON3 = 'GFSv16'
lprmse_hs_HR1_hurricane_JASON3 = 'HR1'
lprmse_hs_HR2_hurricane_JASON3 = 'HR2'
lprmse_hs_HR3a_hurricane_JASON3 = 'HR3a'
lprmse_hs_HR3b_hurricane_JASON3 = 'HR3b'

plot1 = CreatePlot()
plot1.plot_layers = [lprmse_hs_multi1_hurricane_JASON3, lprmse_hs_GFSv16_hurricane_JASON3, lprmse_hs_HR1_hurricane_JASON3, lprmse_hs_HR2_hurricane_JASON3, lprmse_hs_HR3a_hurricane_JASON3, lprmse_hs_HR3b_hurricane_JASON3]
figname='statsrmsehs.png'
    
plot1.add_title('Hurricane JASON3')
plot1.add_xlabel('Forecast Day')
plot1.add_ylabel('RMSE HS')    
plot1.add_legend(loc='upper right')
fig = CreateFigure()
fig.plot_list = [plot1]
fig.create_figure()
fig.save_figure(figname)
fig.close_figure()

