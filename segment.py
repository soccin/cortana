from matplotlib import pyplot as plt
from deepcell.utils.plot_utils import create_rgb_image, make_outline_overlay
from deepcell.applications import Mesmer
import numpy as np
from skimage.io import imread
import os
import sys

def main(argv):
    app = Mesmer()

    compartment="both"
    nuclearFile=sys.argv[1]
    membraneFile=sys.argv[2]

    im1=imread(nuclearFile)
    im2=imread(membraneFile)

    pp=os.path.basename(nuclearFile).split("_")
    sampleId=pp[0]+"_"+pp[1]
    FOV=pp[3]

    outDir=os.path.join("mesmer-output",sampleId,FOV,compartment)
    os.makedirs(outDir,exist_ok=True)

    outInputImage=os.path.join(outDir,sampleId+"_"+FOV+"_input.png")
    outOutputImage=os.path.join(outDir,sampleId+"_"+FOV+"_output.png")
    outSegMaskBase=os.path.join(outDir,sampleId+"_"+FOV)
    
    X = np.stack((im1, im2), axis=-1)
    X = np.expand_dims(X,0)

    rgb_images = create_rgb_image(X, channel_colors=['green', 'blue'])
    fig, ax = plt.subplots(1, 3, figsize=(15, 5))
    ax[0].imshow(X[0, ..., 0], cmap='Greys_r')
    ax[1].imshow(X[0, ..., 1], cmap='Greys_r')
    ax[2].imshow(rgb_images[0, ...])

    ax[0].set_title('Nuclear channel')
    ax[1].set_title('Membrane channel')
    ax[2].set_title('Overlay')

    for a in ax:
        a.axis('off')

    #plt.show()
    fig.savefig(outInputImage)

    segmentation_predictions = app.predict(X, image_mpp=0.325, compartment=compartment)

    segmentation_predictions_wc=np.expand_dims(segmentation_predictions[...,0],3)
    segmentation_predictions_nuc=np.expand_dims(segmentation_predictions[...,1],3)

    overlay_data_wc = make_outline_overlay(
        rgb_data=rgb_images,
        predictions=segmentation_predictions_wc)
    overlay_data_nuc = make_outline_overlay(
        rgb_data=rgb_images,
        predictions=segmentation_predictions_nuc)

    idx = 0

    # plot the data
    fig, ax = plt.subplots(1, 3, figsize=(90,30))
    ax[0].imshow(rgb_images[idx, ...])
    ax[1].imshow(overlay_data_wc[idx, ...])
    ax[2].imshow(overlay_data_nuc[idx, ...])

    ax[0].set_title('Raw data',fontsize=80)
    ax[1].set_title('Whole Cell Predictions',fontsize=80)
    ax[2].set_title('Nuclear Predictions',fontsize=80)

    for a in ax:
        a.axis('off')

    #plt.show()
    fig.savefig(outOutputImage)

    swc=segmentation_predictions_wc[0,...,0]
    np.savetxt(outSegMaskBase+"_wc_seg.csv",swc,delimiter=",",fmt="%d")
    print(",".join(map(str,["NumCells Whole-Cells",sampleId,FOV,np.max(swc)])))

    snuc=segmentation_predictions_nuc[0,...,0]
    np.savetxt(outSegMaskBase+"_nuc_seg.csv",snuc,delimiter=",",fmt="%d")
    print(",".join(map(str,["NumCells Nuclear",sampleId,FOV,np.max(snuc)])))


if __name__ == "__main__":
    main(sys.argv)