/* Simulated annealing search for K33-free 0-1 matrices (Zarankiewicz Z(m,n,3,3) lower bounds).
 * State: n column masks over m rows. Constraint: every row-triple covered by <= 2 columns.
 * Energy = -(ones) + LAM * sum max(0, cov[t]-2). Cell-flip moves, geometric cooling, restarts.
 * Usage: zsearch m n target seconds seed [out.csv]
 * Prints best feasible count found; writes matrix when >= target (and exits 0).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

static int M, N, TARGET;
static double TLIMIT;
static unsigned long long rng;
static inline unsigned long long xr(void){ rng ^= rng<<13; rng ^= rng>>7; rng ^= rng<<17; return rng; }
static inline double frand(void){ return (double)(xr()>>11) / 9007199254740992.0; }

static int triidx[16][16][16];
static int NT;
static int colmask[32];
static signed char cov[600];
static int ones, viol;

static int bestones;
static int bestmask[32];

static void rebuild(void){
    memset(cov,0,sizeof cov); ones=0; viol=0;
    for(int j=0;j<N;j++){
        int mk=colmask[j];
        ones+=__builtin_popcount(mk);
        int bits[16],nb=0;
        for(int r=0;r<M;r++) if(mk>>r&1) bits[nb++]=r;
        for(int a=0;a<nb;a++)for(int b=a+1;b<nb;b++)for(int c=b+1;c<nb;c++){
            int t=triidx[bits[a]][bits[b]][bits[c]];
            cov[t]++; if(cov[t]>2) viol++;
        }
    }
}

/* delta violations if we flip row i in column j (returns dviol; applies to cov if apply=1) */
static inline int flipdelta(int i,int j,int apply){
    int mk=colmask[j];
    int add = !(mk>>i&1);
    int rest = mk & ~(1<<i);
    int dv=0;
    int bits[16],nb=0;
    for(int r=0;r<M;r++) if(rest>>r&1) bits[nb++]=r;
    for(int a=0;a<nb;a++)for(int b=a+1;b<nb;b++){
        int x=bits[a],y=bits[b],t;
        int p=x<i?x:i, q=(x<i? (y<i?y:i) : x), s=(y>i?y:(x>i?x:i));
        /* sort x<y and i into p<q<s */
        if(i<x){p=i;q=x;s=y;} else if(i<y){p=x;q=i;s=y;} else {p=x;q=y;s=i;}
        t=triidx[p][q][s];
        if(add){ if(cov[t]>=2) dv++; if(apply) cov[t]++; }
        else   { if(cov[t]>=3) dv--; if(apply) cov[t]--; }
    }
    return dv;
}

int main(int argc,char**argv){
    if(argc<6){fprintf(stderr,"usage: %s m n target seconds seed [out.csv]\n",argv[0]);return 2;}
    M=atoi(argv[1]); N=atoi(argv[2]); TARGET=atoi(argv[3]);
    TLIMIT=atof(argv[4]); rng=strtoull(argv[5],0,10)*2654435761ULL+88172645463325252ULL;
    const char*outf = argc>6? argv[6] : NULL;

    NT=0;
    for(int a=0;a<M;a++)for(int b=a+1;b<M;b++)for(int c=b+1;c<M;c++)
        triidx[a][b][c]=NT++;

    clock_t t0=clock();
    bestones=0;
    double LAM=3.0;
    while((double)(clock()-t0)/CLOCKS_PER_SEC < TLIMIT){
        /* random restart: random sparse start */
        for(int j=0;j<N;j++){
            int mk=0;
            for(int r=0;r<M;r++) if(frand()<0.25) mk|=1<<r;
            colmask[j]=mk;
        }
        rebuild();
        double T=1.2;
        double cool=0.999995;
        long steps=0;
        while(T>0.015){
            if(((++steps)&1023)==0 && (double)(clock()-t0)/CLOCKS_PER_SEC>TLIMIT) break;
            int i=xr()%M, j=xr()%N;
            int add = !(colmask[j]>>i&1);
            int dv=flipdelta(i,j,0);
            double dE = (add? -1.0: 1.0) + LAM*dv;
            if(dE<=0 || frand()<exp(-dE/T)){
                flipdelta(i,j,1);
                colmask[j]^=1<<i;
                ones+=add?1:-1;
                viol+=dv;
                if(viol==0 && ones>bestones){
                    bestones=ones;
                    memcpy(bestmask,colmask,sizeof colmask);
                    if(bestones>=TARGET) goto done;
                }
            }
            T*=cool;
            /* greedy completion phase at low temperature: try all feasible additions */
            if(T<=0.015 && viol==0){
                int improved=1;
                while(improved){
                    improved=0;
                    for(int jj=0;jj<N;jj++)for(int ii=0;ii<M;ii++){
                        if(colmask[jj]>>ii&1) continue;
                        if(flipdelta(ii,jj,0)==0){
                            flipdelta(ii,jj,1); colmask[jj]|=1<<ii; ones++; improved=1;
                            if(ones>bestones){
                                bestones=ones; memcpy(bestmask,colmask,sizeof colmask);
                                if(bestones>=TARGET) goto done;
                            }
                        }
                    }
                }
            }
        }
    }
done:;
    printf("%d %d best %d target %d %s\n",M,N,bestones,TARGET,bestones>=TARGET?"HIT":"miss");
    if(outf && bestones>0){
        FILE*f=fopen(outf,"w");
        for(int r=0;r<M;r++){
            for(int j=0;j<N;j++) fprintf(f,"%d%s",bestmask[j]>>r&1, j+1<N?",":"");
            fprintf(f,"\n");
        }
        fclose(f);
    }
    return bestones>=TARGET?0:1;
}
