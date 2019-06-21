from some_libs import *
from jreftran_rt import *
import cmath
import argparse

def HeatMap(R,mType,title,xitas,lendas):
    #plt.imshow(R);      plt.show()
    fig, ax = plt.subplots(figsize=(8,8))     #more concise than plt.figure:
    #fig.set_size_inches(18.5, 10.5)
    ax.set_title('Reflectance\n{}'.format(title))
    cmap = 'coolwarm'  # "plasma"  #https://matplotlib.org/examples/color/colormaps_reference.html
    #cmap = sns.cubehelix_palette(start=1, rot=3, gamma=0.8, as_cmap=True)
    if True:
        ticks = np.linspace(0, 1, 10)
        ylabels = [int(i) for i in np.linspace(0, 90, 10)]
        xlabels = [int(i) for i in np.linspace(300, 2000, 10)]
        #cbar_kws={'label': 'Reflex', 'orientation': 'horizontal'}
        # sns.set(font_scale=0.2)
        #  cbar_kws={'label': 'Reflex', 'orientation': 'horizontal'} , center=0.6
        # ax = sns.heatmap(R, square=True, ax=ax, cmap=cmap,yticklabels=ylabels[::-1],xticklabels=xlabels)
        ax = sns.heatmap(R, ax=ax, cmap=cmap,yticklabels=ylabels[::-1],xticklabels=xlabels)
        plt.ylabel('Incident Angle');       plt.xlabel('Wavelength(nm)')
        y_limit = ax.get_ylim();
        x_limit = ax.get_xlim()
        ax.set_yticks(ticks * y_limit[0])
        ax.set_xticks(ticks * x_limit[1])
    else:
        plt.imshow(R)
        ax.set_aspect(256 / 90.0)
        cax = fig.add_axes([0.12, 0.1, 0.78, 0.8])
        cax.get_xaxis().set_visible(False)
        cax.get_yaxis().set_visible(False)
        cax.patch.set_alpha(0)
        cax.set_frame_on(False)
        plt.colorbar(orientation='vertical')

    path = 'E:\MetaLab\hyperbolic\{}\{}.jpg'.format(mType,title)
    plt.savefig(path)
    #plt.show()
    print("")

def N_maters_dict(materials = ['au', 'ag', 'al', 'cu']):
    dict = {}
    for mater in materials:
        N_r_path, N_i_path = './hyperbolic/{}_n1.txt'.format(mater), './hyperbolic/{}_k1.txt'.format(mater)
        fb1 = np.loadtxt(N_r_path)
        fb2 = np.loadtxt(N_i_path)
        n_au = fb1[:, 1] + 1j * fb2[:, 1]
        print(N_r_path, N_i_path)
        dict[mater]=n_au
    return dict

def Hyperbolic_metamaterial_(N_al,N_au,d_al,d_au,polarisation,mType,title,N_dict):
    nm = 1.0e-9
    epsilon0 = 1.0 / (36 * np.pi) * nm                      # dielectric constant of the free space
    lendas = np.arange(300,2010,10)*nm               #300:10:2000[nm]
    if mType != 'random':
        #fb1 = np.loadtxt(N_r_path)        fb2 = np.loadtxt(N_i_path)        n_au = fb1[:,1]+1j*fb2[:,1]
        n_au = N_dict[mType]
    else:
        title=""
    nLenda =len(lendas)
    #t_0 = np.arange(0,90,0.2)
    if False:
        t_0,t1,t2 = np.arange(0,20,1),np.arange(20,40,0.05),np.arange(40,90,1)
        xitas=np.concatenate([t_0,t1,t2])
    else:
        xitas = np.arange(0, 90, 0.1)
        xitas = np.arange(30, 60, 0.001)
    M = len(xitas)
    N = N_al + N_au
    k = 0
    d=np.zeros(N+2)
    d[0] = np.nan
    n_data=np.zeros((nLenda,N+2),dtype=np.complex64)
    for i in range(N): #layer
        if i%2 == 0:
            d[i + 1] = d_au[k] * nm         #% [m]
            if mType == 'random':
                materials = ['au', 'ag', 'al', 'cu']
                mater = random.choice(materials)
                #type = (int)(np.random.uniform(0, len(materials)))
                n_au = N_dict[mater]
                title=title+"{}({})_".format(mater,(int)(d_au[k]))
            n_data[:, i + 1] = n_au[:]
        else:
            d[i + 1] = d_al[k] * nm         #% [m]
            n_data[:, i + 1] = 1.46         #SiO2
            title = title + "{}_".format((int)(d_al[k]))
            k = k + 1;
    title="{}nm [{}]".format(np.sum(d_au)+np.sum(d_al),title)

    n_data[:, 0] = 1.77     #Al2O3
    d[N+1]=np.nan
    n_data[:,N+1] = 1       #air
    #print("lenda={}\nd={}\nn_data={}\nxitas={}".format(lendas,d,n_data,xitas))
    r = np.zeros((M,nLenda),dtype=np.complex64);
    t = np.zeros((M,nLenda),dtype=np.complex64);
    R=np.zeros((M,nLenda))
    T = np.zeros((M,nLenda));
    A= np.zeros((M,nLenda))
    if False:
        for i in range(nLenda):                      #wavelength's number
            n_ = n_data[i,:]
            r, t, R, T, A = jreftran_rt_vector(lendas[i],d,n_data[i,:],xitas,polarisation)
    else:
        for i in range(nLenda):                   #wavelength's number
            for j in range(M):              #angle
                #the refractive index of the each layer
                #Complex refractive index for eatch layer
                row = (int)(M-1-j);  col=(int)(i)   #数据格式原因
                r[row,col], t[row,col], R[row,col], T[row,col], A[row,col] = jreftran_rt(lendas[i],d,n_data[i,:],xitas[j],polarisation)
    print("")
    HeatMap(R,mType,title,xitas,lendas)

def parse_args():
    parser = argparse.ArgumentParser('Metlab Hyperbolic')
    parser.add_argument('-c', '--cuda', action='store_true',
        help='whether use gpu to train network')
    parser.add_argument('-g', '--gpu', type=str, default='0',
        help='the gpu id to train net')
    parser.add_argument('-m', '--model', type=str, default='model/bdcn_pretrained_on_bsds500.pth',#'params/bdcn_final.pth',
        help='the model to test')
    parser.add_argument('--res-dir', type=str, default='result',
        help='the dir to store result')
    parser.add_argument('-layers', type=int, default=5,help='the number of layers')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    N_case,case = 1000,0
    mType = 'random'        #'al'
    #ud_au = 5  # 金属厚度[nm]
    N_dict = N_maters_dict()
    N_di = args.layers # 模型介质层数
    N_al, N_au = N_di, N_di
    d_al_TM = None  # randi([50, 1680], 1, N_al). / 10; % 168 =（300 - 25） / 1.44
    d_au = None
    polarisation = 1  # TM

    # N_r_path,N_i_path = './hyperbolic/cu_n1.txt','./hyperbolic/cu_k1.txt'
    #d_au = ud_au * np.ones(N_au)
    # d_al_TM = np.array([52.2,16.1,18.8,16.1,71.8])
    d_al_TM = []
    random.seed(42)
    while case <N_case:
        d_al_TM = None  #randi([50, 1680], 1, N_al). / 10; % 168 =（300 - 25） / 1.44
        d_au = None
        t0=time.time()
        #N_r_path,N_i_path = './hyperbolic/cu_n1.txt','./hyperbolic/cu_k1.txt'
        #d_au = ud_au * np.ones(N_au)
        #d_al_TM = np.array([52.2,16.1,18.8,16.1,71.8])
        d_au,d_al_TM=[],[]
        sum = 0
        for no in range(N_au):
            h=random.uniform(5, 10)
            d_au.append((int)(h))
            sum = sum+h
        for no in range(N_di):
            #hSi = random.uniform(5, 168)
            hSi = random.uniform(5, 300-sum)
            d_al_TM.append((int)(hSi))
            sum = sum+hSi
            if sum>=300-5:
                break
        title="{}_{}".format(mType,d_al_TM)
        #if sum * 1.46 < (300 - 25):
        if sum * 1.46 < (300):
            Hyperbolic_metamaterial_(N_al, N_au, d_al_TM, d_au, polarisation, mType, title, N_dict)
            print("{}:\t{:.4g} sum={} d={},{}".format(case,time.time()-t0,sum,d_au,d_al_TM))
            case = case+1
