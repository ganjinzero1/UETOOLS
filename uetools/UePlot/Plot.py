# Object for plotting 
from matplotlib.pyplot import ion
ion()

class Plot():
    def __init__(self, rm=None, zm=None):
        ''' Constructs patches objects
        rm - UEDGE R-node object
        zm - UEDGE Z-node object
        '''
        # Intialize empty
        if (rm is None) or (zm is None):
            try:
                rm = self.get('rm')
                zm = self.get('zm')
            except:
                return
        # TODO: implement handling of USN geometries -> Plot flipped
            

        self.vertices = self.createpolycollection(rm, zm)
        
        if self.getue('geometry')[0].strip().lower().decode('UTF-8') == \
            'uppersn':
            self.disp = 0
            if self.get('rmagx') + self.get('zmagx') == 0:
                self.disp = -(-zm).min()
            else:
                self.disp = 2*self.get(zmagx)
            self.uppersnvertices = self.createpolycollection(rm, \
                -zm + self.disp, setparams=False)
        return
 
    def createpolycollection(self, rm, zm, margins=0.05, setparams=True):
        ''' Creates a poly collection and records boundaries
        ''' 
        from matplotlib.collections import PolyCollection
        from uedge import com

        if setparams is True:
            self.nx = rm.shape[0]-2
            self.ny = rm.shape[1]-2
            # TODO: where to pass/find xpoint indices?
            self.isepr = rm[1:self.get('ixpt1')[0]+2,self.get('iysptrx')+1, 1]
            self.isepz = zm[1:self.get('ixpt1')[0]+2,self.get('iysptrx')+1, 1]
            self.osepr = rm[self.get('ixpt2')[0]:-1,self.get('iysptrx')+1, 2]
            self.osepz = zm[self.get('ixpt2')[0]:-1,self.get('iysptrx')+1, 2]

        vertices = []
        # Loop through all cells, omitting guard cells
        for i in range(1,len(rm)-1):
            for j in range(1,len(rm[i])-1):
                vert = []
                for k in [1, 2, 4, 3]:
                    vert.append([rm[i, j, k], zm[i, j, k]]) 
                vertices.append(vert)
        return PolyCollection(vertices)

    def checkusn(self, array, flip=False):
        if flip is False:
            return array
        elif (self.getue('geometry')[0].strip().lower().decode('UTF-8') == \
            'uppersn'):
            return -array + self.disp

    def plotprofile(self, x, y, ax=None, xlim=(None, None), ylim=(0, None),
        figsize=(6,5), xlabel=None, ylabel=None, title=None, logx=False, 
        logy=False, color='k', **kwargs):
        ''' Plots y as function of x '''
        from matplotlib.pyplot import figure, Axes, Figure

        if ax is None: # Create figure if no axis supplied
            f = figure(title, figsize=figsize)
            ax = f.add_subplot()
        elif ax is Figure:
            ax = ax.get_axes()[0]
        # Switch to identify requested plot type
        if logx and logy:
            plot = ax.loglog
        elif logx and not logy:
            plot = ax.semilogx
        elif logy and not logx:
            plot = ax.semilogy
        else:
            plot = ax.plot
    
        plot(x, y, color=color, **kwargs)

        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        return ax.get_figure()

    def plotmesh(self, z=None, rm=None, zm=None, ax=None, linewidth=0.2,
        linecolor='k', aspect='equal', figsize=(5,7), cmap='magma', units='', 
        xlim=(None, None), ylim=(None, None), zrange=(None, None), 
        log=False, vessel=True, plates=True, lcfs=True, title=None, 
        grid=False, flip=False):
        ''' General plotting function
        z - values, if any. If None, plots grid
        rm, zm - radial and horizontal nodes
        '''
        from matplotlib.pyplot import figure, Figure
        from matplotlib.colors import LogNorm
        from copy import deepcopy
        from numpy import array
        from uedge import com, bbb, grd        

        if ax is None:
            f = figure(title, figsize=figsize)
            ax = f.add_subplot()
        if ax is Figure:
            ax = ax.get_axes()[0]
        if (rm is None) or (zm is None):
            # Use stored PolyCollection
            if (self.getue('geometry')[0].strip().lower().decode('UTF-8') == \
                'uppersn') and (flip is True): 
                vertices = deepcopy(self.uppersnvertices)
            else:
                vertices = deepcopy(self.vertices)
        else: # Create collection from data
            vertices = self.createpolycollection(rm, zm)
        if grid is False:
            vertices.set_linewidths(1)
            vertices.set_edgecolors('face')
        else:
            vertices.set_edgecolors(linecolor)
            vertices.set_linewidths(linewidth)
        if z is None: # Plot grid
            vertices.set_facecolor((0, 0, 0, 0))
            vertices.set_edgecolors(linecolor)
            vertices.set_linewidths(linewidth)
        else:
            vertices.set_cmap(cmap)
            vertices.set_array(z[1:-1,1:-1].reshape(self.nx*self.ny))
            vertices.set_clim(*zrange)
            if log is True:
                vertices.set_norm(LogNorm())
            
        ax.add_collection(vertices)
        # TODO: devise scheme to look for variables in memory, from 
        # Forthon, from HDF5
        if lcfs is True:
            self.plotlcfs(ax, flip)
        if vessel is True:
            self.plotvessel(ax, flip)
        if plates is True:
            self.plotplates(ax, flip)
        ax.autoscale_view()
        ax.set_title(title)
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.set_xlabel('R [m]')
        ax.set_ylabel('Z [m]')
        ax.set_aspect(aspect)
        if z is not None:
            cbar = ax.get_figure().colorbar(vertices, ax=ax)
            cbar.ax.set_ylabel(units, va='bottom')
        return ax.get_figure()
           

    def plotlcfs(self, ax, flip=False, color='grey', linewidth=0.5,
        **kwargs):
        """ Plots LCFS on ax """
        from uedge import com, bbb, grd        
        
        if self.get('geometry')[0].strip().lower().decode('UTF-8') == 'dnull':
            rm = self.get('rm')
            zm = self.get('zm')
            iysptrx1 = self.get('iysptrx1')
            iysptrx2 = self.get('iysptrx2')
            ixrb = self.get('ixrb')
            ixlb = self.get('ixlb')
            ixpt1 = self.get('ixpt1')
            ixpt2 = self.get('ixpt2')

            ax.plot(rm[:ixrb[0]+1, iysptrx1[0]+1, 1],
                zm[:ixrb[0]+1, iysptrx1[0]+1, 1], color=color, 
                linewidth=linewidth)
            ax.plot(rm[ixlb[1]:, iysptrx1[0]+1, 1],
                zm[ixlb[1]:, iysptrx1[0]+1, 1], color=color, 
                linewidth=linewidth)

            ax.plot(rm[:ixpt1[0]+1, iysptrx2[0]+1, 2],
                zm[:ixpt1[0]+1, iysptrx2[0]+1, 2], 
                color=color, linewidth=linewidth)
            ax.plot(rm[ixpt2[1]+1:, iysptrx2[0]+1, 1],
                zm[ixpt2[1]+1:, iysptrx2[0]+1, 1], 
                color=color, linewidth=linewidth)
        
            ax.plot(rm[ixpt1[0]+1:ixrb[0]+1, iysptrx2[0]+1, 1],
                zm[ixpt1[0]+1:ixrb[0]+1, iysptrx2[0]+1, 1], 
                color=color, linewidth=linewidth)
            ax.plot(rm[ixlb[1]:ixpt2[1]+1, iysptrx2[0]+1, 2],
                zm[ixlb[1]:ixpt2[1]+1, iysptrx2[0]+1, 2], 
                color=color, linewidth=linewidth)

        else:
            plotted = False
            try:
                ax.plot(com.rbdry, self.checkusn(com.zbdry, flip), 
                    color=color, linewidth=linewidth)
                ax.plot(self.isepr, self.checkusn(self.isepz, flip), 
                    color=color, linewidth=linewidth)
                ax.plot(self.osepr, self.checkusn(self.osepz, flip), 
                color=color, linewidth=linewidth)
                plotted = True
            except:
                pass
            try:
                if self.get('rbdry') != False:
                    ax.plot(self.get('rbdry'), self.checkusn(self.get(\
                        'zbdry'), flip), color=color, 
                        linewidth=linewidth)
                    ax.plot(self.isepr, self.checkusn(self.isepz, flip), 
                        color=color, linewidth=linewidth)
                    ax.plot(self.osepr, self.checkusn(self.osepz, flip), 
                        color=color, linewidth=linewidth)
                    plotted = True
            except:
                pass
            if plotted is False:
                ax.plot(self.get('rm')[com.ixpt1[0]:com.ixpt2[0]+1,\
                    com.iysptrx+1,2], self.checkusn(self.get('zm')[\
                    com.ixpt1[0]:com.ixpt2[0]+1,com.iysptrx+1,2], flip),
                    color=color, linewidth=linewidth)
                ax.plot(self.isepr, self.checkusn(self.isepz, flip), 
                    color=color, linewidth=linewidth)
                ax.plot(self.osepr, self.checkusn(self.osepz, flip), 
                    color=color, linewidth=linewidth)

    def plotvessel(self, ax, flip=False):
        """ Plots vessel on ax """
        from uedge import com, bbb, grd        
        try:
            ax.plot(com.xlim, self.checkusn(com.ylim, flip), 'k-', 
                linewidth=3)
            ax.plot(com.xlim, self.checkusn(com.ylim, flip), 
                'y-', linewidth=1)
        except:
            pass
        try:
            if self.get('xlim') != False:
                ax.plot(self.get('xlim'), self.checkusn(self.get('ylim'), 
                    flip), 'k-', linewidth=3)
                ax.plot(self.get('xlim'), self.checkusn(self.get('ylim'), 
                    flip), 'y-', linewidth=1)
        except:
            pass

    def plotplates(self, ax, flip=False):
        """ Plot plates on ax """    
        from uedge import com, bbb, grd        
        try:
            ax.plot(grd.rplate1, self.checkusn(grd.zplate1, flip), 'b-', 
                linewidth=1.5)
            ax.plot(grd.rplate2, self.checkusn(grd.zplate2, flip), 'r-', 
                linewidth=1.5)
        except:
            pass
        try:
            if self.get('rplate1') != False:
                ax.plot(self.get('rplate1'), self.checkusn(self.get(\
                    'zplate1'), flip), 'b-', linewidth=1.5)
                ax.plot(self.get('rplate2'), self.checkusn(self.get(\
                    'zplate2'), flip), 'r-', linewidth=1.5)
        except:
            pass
