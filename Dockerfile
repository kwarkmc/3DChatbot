FROM nvidia/cuda:11.3.1-devel-ubuntu20.04

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV PATH /opt/conda/bin:$PATH

# Install dependencies of Miniconda

RUN apt-get update --fix-missing && \
    apt-get install -y wget bzip2 ca-certificates curl git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Miniconda

RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh && \
    #/opt/conda/bin/conda clean -tipsy && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate T2M-GPT" >> ~/.bashrc

#Install Environment.yaml

COPY ./environment.yml /tmp/environment.yaml
RUN /opt/conda/bin/conda env create -f /tmp/environment.yaml

SHELL ["/bin/bash", "-c"]
RUN echo "source activate T2M-GPT" >> ~/.bashrc

RUN /bin/bash -c "source activate T2M-GPT"

# Install SSH

RUN echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config && \
    echo "PermitRootLogin yes" >> /etc/ssh/sshd_config && \
    echo "UsePAM no" >> /etc/ssh/sshd_config

#Normal User Create

# ARG UID=
# ARG USER_NAME=

# RUN adduser $USER_NAME -u $UID --quiet --gecos "" --disabled-password && \
#     echo "$USER_NAME ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/$USER_NAME && \
#     chmod 0440 /etc/sudoers.d/$USER_NAME

# # Install JupyterNotebook

# RUN source activate ${T2M-GPT} && \
#     conda install -c conda-forge jupyterlab && \
#     jupyter serverextension enable --py jupyterlab --sys-prefix

CMD [ "/bin/bash" ]