/* Degree-constrained annealer for K33-free matrices.
 * Columns have FIXED degrees (given profile). Move: swap a 1 to a 0 within a column.
 * Energy = sum max(0, cov[t]-2) over row triples. Feasible (E=0) => matrix with sum(d) ones.
 * Usage: zsearch2 m n "d1xk1,d2xk2,..." seconds seed [out.csv]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

static int M,N;
static double TLIMIT;
static unsigned long long rng;
static inline unsigned long long xr(void){ rng^=rng<<13; rng^=rng>>7; rng^=rng<<17; return rng; }
static inline double frand(void){ return (double)(xr()>>11)/9007199254740992.0; }

static int triidx[24][24][24];
static int colmask[32], coldeg[32];
static signed char cov[2100];
static int viol;

static void rebuild(void){
    memset(cov,0,sizeof cov); viol=0;
    for(int j=0;j<N;j++){
        int bits[24],nb=0,mk=colmask[j];
        for(int r=0;r<M;r++) if(mk>>r&1) bits[nb++]=r;
        for(int a=0;a<nb;a++)for(int b=a+1;b<nb;b++)for(int c=b+1;c<nb;c++){
            int t=triidx[bits[a]][bits[b]][bits[c]];
            cov[t]++; if(cov[t]>2) viol++;
        }
    }
}

static inline int tri3(int a,int b,int c){
    int p,q,s;
    if(a>b){int z=a;a=b;b=z;}
    if(b>c){int z=b;b=c;c=z;}
    if(a>b){int z=a;a=b;b=z;}
    p=a;q=b;s=c;
    return triidx[p][q][s];
}

/* delta-viol for removing row i then adding row k in column j; apply if flag set */
static inline int swapdelta(int j,int i,int k,int apply){
    int rest = colmask[j] & ~(1<<i);   /* k not in rest */
    int bits[24],nb=0,dv=0;
    for(int r=0;r<M;r++) if(rest>>r&1) bits[nb++]=r;
    for(int a=0;a<nb;a++)for(int b=a+1;b<nb;b++){
        int t1=tri3(bits[a],bits[b],i);
        int t2=tri3(bits[a],bits[b],k);
        if(t1==t2) continue;
        if(cov[t1]>=3) dv--;
        if(apply) cov[t1]--;
        if(cov[t2]>=2) dv++;
        if(apply) cov[t2]++;
    }
    return dv;
}

int main(int argc,char**argv){
    if(argc<6){fprintf(stderr,"usage: %s m n profile seconds seed [out.csv]\n",argv[0]);return 2;}
    M=atoi(argv[1]); N=atoi(argv[2]);
    char*prof=argv[3];
    TLIMIT=atof(argv[4]); rng=strtoull(argv[5],0,10)*2654435761ULL+88172645463325252ULL;
    const char*outf=argc>6?argv[6]:NULL;

    int nc=0;
    {
        char*p=strdup(prof), *tok=strtok(p,",");
        while(tok){ int d,k; sscanf(tok,"%dx%d",&d,&k);
            for(int i=0;i<k;i++){ coldeg[nc]=d; nc++; }
            tok=strtok(0,","); }
    }
    if(nc!=N){fprintf(stderr,"profile has %d cols, expected %d\n",nc,N);return 2;}
    int NT=0;
    for(int a=0;a<M;a++)for(int b=a+1;b<M;b++)for(int c=b+1;c<M;c++) triidx[a][b][c]=NT++;

    clock_t t0=clock();
    int bestviol=1<<30, bestmask[32];
    while((double)(clock()-t0)/CLOCKS_PER_SEC<TLIMIT){
        for(int j=0;j<N;j++){
            int mk=0,need=coldeg[j];
            while(__builtin_popcount(mk)<need) mk|=1<<(xr()%M);
            colmask[j]=mk;
        }
        rebuild();
        double T=0.9, cool=0.999996;
        long stale=0;
        while(T>0.008 && viol>0){
            if((stale&2047)==0 && (double)(clock()-t0)/CLOCKS_PER_SEC>TLIMIT) break;
            stale++;
            int j=xr()%N;
            if(coldeg[j]==0||coldeg[j]==M) continue;
            int inb[24],ni=0,outb[24],no=0;
            for(int r=0;r<M;r++){ if(colmask[j]>>r&1) inb[ni++]=r; else outb[no++]=r; }
            int i=inb[xr()%ni], k=outb[xr()%no];
            int dv=swapdelta(j,i,k,0);
            if(dv<=0 || frand()<exp(-dv/T)){
                swapdelta(j,i,k,1);
                colmask[j] = (colmask[j]&~(1<<i))|(1<<k);
                viol+=dv;
            }
            T*=cool;
            if(T<=0.02 && viol>0 && (stale%1500000)==0) T=0.45; /* reheat */
        }
        if(viol<bestviol){ bestviol=viol; memcpy(bestmask,colmask,sizeof colmask); }
        if(viol==0) break;
    }
    int ones=0; for(int j=0;j<N;j++) ones+=coldeg[j];
    printf("%d %d profile %s viol %d %s\n",M,N,prof,bestviol,bestviol==0?"HIT":"miss");
    if(outf && bestviol==0){
        FILE*f=fopen(outf,"w");
        for(int r=0;r<M;r++){
            for(int j=0;j<N;j++) fprintf(f,"%d%s",bestmask[j]>>r&1,j+1<N?",":"");
            fprintf(f,"\n");
        }
        fclose(f);
    }
    (void)ones;
    return bestviol==0?0:1;
}
