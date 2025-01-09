from matplotlib import pyplot as plt
from deepcell.utils.plot_utils import create_rgb_image, make_outline_overlay
from deepcell.applications import Mesmer
import numpy as np
from skimage.io import imread
import os
import sys

def main(argv):
    app = Mesmer()

    nuclearFile=sys.argv[1]
    membraneFile=sys.argv[2]

    im1=imread(nuclearFile)
    im2=imread(membraneFile)

    pp=os.path.basename(nuclearFile).split("_")
    sampleId=pp[0]+"_"+pp[1]
    FOV=pp[3]

    outDir=os.path.join("mesmer-output",sampleId,FOV)
    os.makedirs(outDir,exist_ok=True)

    outInputImage=os.path.join(outDir,sampleId+"_"+FOV+"_input.png")
    outOutputImage=os.path.join(outDir,sampleId+"_"+FOV+"_output.png")
    outSegMask=os.path.join(outDir,sampleId+"_"+FOV+"_seg.csv")
    
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

    segmentation_predictions_nuc = app.predict(X, image_mpp=0.325, compartment='nuclear')

    overlay_data_nuc = make_outline_overlay(
        rgb_data=rgb_images,
        predictions=segmentation_predictions_nuc)

    idx = 0

    # plot the data
    fig, ax = plt.subplots(1, 2, figsize=(100, 50))
    ax[0].imshow(rgb_images[idx, ...])
    ax[1].imshow(overlay_data_nuc[idx, ...])

    ax[0].set_title('Raw data')
    ax[1].set_title('Nuclear Predictions')

    for a in ax:
        a.axis('off')

    #plt.show()
    fig.savefig(outOutputImage)

    s1=segmentation_predictions_nuc[0,...,0]
    np.savetxt(outSegMask,s1,delimiter=",",fmt="%d")
    print(",".join(map(str,["NumCells",sampleId,FOV,np.max(s1)])))

if __name__ == "__main__":
    main(sys.argv)