from files.models import Files
from utils.utils import compressImage, logger


def imageWorker(request, property):
    if request.FILES:
        images_data = request.FILES.getlist("images")
        files_list = []

        logger.info(images_data)

        for property_image in images_data:
            compressed_image_io = compressImage(property_image)
            logger.info("Compressed Image")  # Add this line to debug
            files_list.append(Files(file_url=compressed_image_io))

        if files_list:
            images = Files.objects.bulk_create(files_list)
            logger.info("Images Created")  # Add this line to debug
            
            for image in images:
                property.images.add(image.id)